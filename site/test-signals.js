(() => {
  'use strict';

  const form = document.querySelector('[data-signal-form]');
  if (!form) return;

  const preview = document.querySelector('[data-signal-preview]');
  const download = document.querySelector('[data-signal-download]');
  const status = document.querySelector('[data-signal-status]');
  const meta = {
    type: document.querySelector('[data-meta-type]'),
    rate: document.querySelector('[data-meta-rate]'),
    level: document.querySelector('[data-meta-level]'),
  };
  let objectUrl = null;

  const clamp = (value, min, max) => Math.min(max, Math.max(min, value));
  const peakForDbfs = (db) => Math.pow(10, db / 20);

  function applyEdgeFade(value, frame, total, sampleRate) {
    const fadeFrames = Math.max(1, Math.round(sampleRate * 0.02));
    let gain = 1;
    if (frame < fadeFrames) gain = frame / fadeFrames;
    if (frame >= total - fadeFrames) gain = Math.min(gain, (total - frame - 1) / fadeFrames);
    return value * clamp(gain, 0, 1);
  }

  function writeAscii(view, offset, text) {
    for (let i = 0; i < text.length; i += 1) view.setUint8(offset + i, text.charCodeAt(i));
  }

  function encodeWav(channels, sampleRate) {
    const channelCount = channels.length;
    const frames = channels[0].length;
    const bytesPerSample = 2;
    const dataBytes = frames * channelCount * bytesPerSample;
    const buffer = new ArrayBuffer(44 + dataBytes);
    const view = new DataView(buffer);

    writeAscii(view, 0, 'RIFF');
    view.setUint32(4, 36 + dataBytes, true);
    writeAscii(view, 8, 'WAVE');
    writeAscii(view, 12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, 1, true);
    view.setUint16(22, channelCount, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * channelCount * bytesPerSample, true);
    view.setUint16(32, channelCount * bytesPerSample, true);
    view.setUint16(34, 16, true);
    writeAscii(view, 36, 'data');
    view.setUint32(40, dataBytes, true);

    let offset = 44;
    for (let frame = 0; frame < frames; frame += 1) {
      for (let ch = 0; ch < channelCount; ch += 1) {
        const sample = clamp(channels[ch][frame], -1, 1);
        view.setInt16(offset, sample < 0 ? Math.round(sample * 32768) : Math.round(sample * 32767), true);
        offset += 2;
      }
    }
    return new Blob([buffer], { type: 'audio/wav' });
  }

  function normalizePeak(channels, targetPeak) {
    let maxPeak = 0;
    for (const channel of channels) {
      for (let i = 0; i < channel.length; i += 1) maxPeak = Math.max(maxPeak, Math.abs(channel[i]));
    }
    if (maxPeak <= 0) return channels;
    const gain = targetPeak / maxPeak;
    for (const channel of channels) {
      for (let i = 0; i < channel.length; i += 1) channel[i] *= gain;
    }
    return channels;
  }

  function deterministicPink(frames, sampleRate, targetPeak) {
    const out = new Float32Array(frames);
    let seed = 0x61850;
    let b0 = 0, b1 = 0, b2 = 0, b3 = 0, b4 = 0, b5 = 0, b6 = 0;
    for (let i = 0; i < frames; i += 1) {
      seed = (1664525 * seed + 1013904223) >>> 0;
      const white = (seed / 4294967295) * 2 - 1;
      b0 = 0.99886 * b0 + white * 0.0555179;
      b1 = 0.99332 * b1 + white * 0.0750759;
      b2 = 0.96900 * b2 + white * 0.1538520;
      b3 = 0.86650 * b3 + white * 0.3104856;
      b4 = 0.55000 * b4 + white * 0.5329522;
      b5 = -0.7616 * b5 - white * 0.0168980;
      const pink = b0 + b1 + b2 + b3 + b4 + b5 + b6 + white * 0.5362;
      b6 = white * 0.115926;
      out[i] = applyEdgeFade(pink * 0.11, i, frames, sampleRate);
    }
    return normalizePeak([out], targetPeak);
  }

  function generate(type, duration, sampleRate, levelDbfs) {
    const frames = Math.max(1, Math.round(duration * sampleRate));
    const targetPeak = peakForDbfs(levelDbfs);

    if (type === 'pink') return deterministicPink(frames, sampleRate, targetPeak);

    if (type === 'channels' || type === 'phase') {
      const left = new Float32Array(frames);
      const right = new Float32Array(frames);
      for (let i = 0; i < frames; i += 1) {
        const t = i / sampleRate;
        const tone = Math.sin(2 * Math.PI * 440 * t) * targetPeak;
        const p = i / frames;
        if (type === 'channels') {
          const segment = Math.min(3, Math.floor(p * 4));
          const lOn = segment === 0 || segment === 1 || segment === 3;
          const rOn = segment === 0 || segment === 2 || segment === 3;
          left[i] = applyEdgeFade(lOn ? tone : 0, i, frames, sampleRate);
          right[i] = applyEdgeFade(rOn ? tone : 0, i, frames, sampleRate);
        } else {
          left[i] = applyEdgeFade(tone, i, frames, sampleRate);
          right[i] = applyEdgeFade(p < 0.5 ? tone : -tone, i, frames, sampleRate);
        }
      }
      return [left, right];
    }

    const mono = new Float32Array(frames);
    for (let i = 0; i < frames; i += 1) {
      const t = i / sampleRate;
      let value = 0;
      if (type === 'sine1k') {
        value = Math.sin(2 * Math.PI * 1000 * t) * targetPeak;
      } else {
        const f0 = 20;
        const f1 = Math.min(20000, sampleRate * 0.45);
        const ratio = f1 / f0;
        const phase = 2 * Math.PI * f0 * duration / Math.log(ratio) * (Math.pow(ratio, t / duration) - 1);
        value = Math.sin(phase) * targetPeak;
      }
      mono[i] = applyEdgeFade(value, i, frames, sampleRate);
    }
    return [mono];
  }

  function labelFor(type) {
    return {
      sine1k: '1 kHz sine reference',
      sweep: '20 Hz–20 kHz logarithmic sweep',
      pink: 'Deterministic pink noise',
      channels: 'Stereo left/right channel check',
      phase: 'In-phase / polarity-inverted check',
    }[type] || type;
  }

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = new FormData(form);
    const type = String(data.get('signal') || 'sine1k');
    const duration = clamp(Number(data.get('duration')) || 5, 1, 30);
    const sampleRate = [44100, 48000, 96000].includes(Number(data.get('sampleRate'))) ? Number(data.get('sampleRate')) : 48000;
    const levelDbfs = clamp(Number(data.get('level')) || -24, -60, -6);

    status.textContent = 'Generating locally in your browser…';
    window.setTimeout(() => {
      const channels = generate(type, duration, sampleRate, levelDbfs);
      const blob = encodeWav(channels, sampleRate);
      if (objectUrl) URL.revokeObjectURL(objectUrl);
      objectUrl = URL.createObjectURL(blob);
      preview.src = objectUrl;
      preview.load();
      const safeName = `arsonkupik-${type}-${sampleRate}hz-${Math.abs(levelDbfs)}dbfs.wav`;
      download.href = objectUrl;
      download.download = safeName;
      download.hidden = false;
      meta.type.textContent = labelFor(type);
      meta.rate.textContent = `${sampleRate.toLocaleString()} Hz / 16-bit PCM`;
      meta.level.textContent = `${levelDbfs} dBFS peak ceiling`;
      status.textContent = 'WAV ready. Preview quietly or download for a controlled test.';
    }, 0);
  });

  window.addEventListener('beforeunload', () => {
    if (objectUrl) URL.revokeObjectURL(objectUrl);
  });
})();
