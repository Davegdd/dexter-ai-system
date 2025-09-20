import librosa
import numpy as np
import soundfile as sf
from scipy import signal
from scipy.signal import butter, lfilter
import time
import logging
from typing import Tuple, Union

logger = logging.getLogger(__name__)

class VoiceDistortor:
    def __init__(self, sample_rate: int = 22050):
        self.sr = sample_rate
    
    def load_audio(self, file_path: str) -> Tuple[np.ndarray, int]:
        """Load audio file"""
        audio, sr = librosa.load(file_path, sr=self.sr)
        return audio, sr
    
    def pitch_shift(self, audio: np.ndarray, semitones: Union[int, float]) -> np.ndarray:
        """Shift pitch by semitones (negative for deeper voice)"""
        return librosa.effects.pitch_shift(audio, sr=self.sr, n_steps=semitones)
    
    def formant_shift(self, audio: np.ndarray, shift_factor: Union[int, float] = 0.8) -> np.ndarray:
        """Shift formants to create robotic effect"""
        stft = librosa.stft(audio)
        magnitude = np.abs(stft)
        phase = np.angle(stft)
        
        shifted_mag = np.zeros_like(magnitude)
        for i, frame in enumerate(magnitude.T):
            indices = np.arange(len(frame)) * shift_factor
            shifted_mag[:, i] = np.interp(np.arange(len(frame)), indices, frame)
        
        shifted_stft = shifted_mag * np.exp(1j * phase)
        return librosa.istft(shifted_stft)
    
    def add_distortion(self, audio: np.ndarray, gain: Union[int, float] = 2.0, threshold: Union[int, float] = 0.3) -> np.ndarray:
        """Add distortion/saturation for evil character"""
        distorted = audio * gain
        
        distorted = np.tanh(distorted)
        
        distorted = np.clip(distorted, -threshold, threshold)
        
        return distorted
    
    def add_reverb(self, audio: np.ndarray, room_size: Union[int, float] = 0.8, damping: Union[int, float] = 0.5) -> np.ndarray:
        """Add reverb for atmospheric effect"""
        ir_length = int(self.sr * 2)
        ir = np.random.randn(ir_length) * np.exp(-np.arange(ir_length) / (self.sr * room_size))
        ir *= damping
        
        reverbed = signal.convolve(audio, ir, mode='same')
        
        return 0.7 * audio + 0.3 * reverbed
    
    def vocoder_effect(self, audio: np.ndarray, bands: int = 10) -> np.ndarray:
        """Create vocoder-like effect"""
        nyquist = self.sr / 2
        band_edges = np.logspace(np.log10(100), np.log10(nyquist), bands + 1)
        
        processed_bands = []
        
        for i in range(bands):
            low = band_edges[i] / nyquist
            high = band_edges[i + 1] / nyquist
            
            if high >= 1.0:
                high = 0.99
            
            b, a = butter(4, [low, high], btype='band')
            band_signal = lfilter(b, a, audio)
            
            envelope = np.abs(signal.hilbert(band_signal))
            kernel_size = int(self.sr * 0.01)
            if kernel_size % 2 == 0:
                kernel_size += 1
            envelope = signal.medfilt(envelope, kernel_size=kernel_size)
            
            modulation_freq = 100 + i * 50
            t = np.arange(len(audio)) / self.sr
            modulator = signal.square(2 * np.pi * modulation_freq * t) * 0.5 + 0.5
            
            processed_band = envelope * modulator * np.sign(band_signal)
            processed_bands.append(processed_band)
        
        return np.sum(processed_bands, axis=0)
    
    def apply_eq(self, audio: np.ndarray, bass_gain: Union[int, float] = 3.0, mid_gain: Union[int, float] = 0.5, treble_gain: Union[int, float] = 1.5) -> np.ndarray:
        """Apply EQ to enhance the evil character"""
        bass_freq = 150
        treble_freq = 3000
        
        bass_b, bass_a = butter(2, bass_freq / (self.sr / 2), btype='low')
        treble_b, treble_a = butter(2, treble_freq / (self.sr / 2), btype='high')
        
        bass = lfilter(bass_b, bass_a, audio) * bass_gain
        treble = lfilter(treble_b, treble_a, audio) * treble_gain
        mid = audio * mid_gain
        
        return bass + mid + treble
    
    def create_robot_voice(self, audio: np.ndarray) -> np.ndarray:
        """Apply robot voice effects"""
        result = audio.copy()
        
        result = self.pitch_shift(result, -2)
        result = self.apply_eq(result, bass_gain=2.0, mid_gain=1.0, treble_gain=2.0)
        
        result = result / np.max(np.abs(result)) * 0.95
        
        return result
    
    def process_file(self, input_path: str, output_path: str):
        """Process an audio file and save the result"""
        start_time = time.time()
        
        logger.info(f"Loading audio from: {input_path}")
        load_start = time.time()
        audio, sr = self.load_audio(input_path)
        load_time = time.time() - load_start
        logger.info(f"Audio loaded in {load_time:.2f} seconds")
        
        logger.info("Applying robot voice distortion...")
        process_start = time.time()
        processed_audio = self.create_robot_voice(audio)
        process_time = time.time() - process_start
        logger.info(f"Robot preset applied in {process_time:.2f} seconds")
        
        logger.info(f"Saving processed audio to: {output_path}")
        save_start = time.time()
        sf.write(output_path, processed_audio, sr)
        save_time = time.time() - save_start
        logger.info(f"Audio saved in {save_time:.2f} seconds")
        
        total_time = time.time() - start_time
        logger.info(f"Total processing time: {total_time:.2f} seconds")
        logger.info("Processing complete!")
        logger.info("-" * 50)