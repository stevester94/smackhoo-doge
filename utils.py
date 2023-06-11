import numpy as np

class UltraSigGen:
    def __init__( self, frequency, sampleRate, phase_rads=0 ) -> None:

        self.theta = phase_rads
        self.amplitude = 0.999
        self.frequency = frequency
        self.sampleRate = sampleRate

        self.last_n = -1
        self.last_t = None
    def get( self, n )->np.ndarray:
        # We can cache the t vector and reuse if n stays the same (~50% speed increase!)
        if n != self.last_n:
            t = np.arange( n ) * (1/self.sampleRate)
            self.last_n = n
            self.last_t = t
        else:
            t = self.last_t
        out = self.amplitude * np.sin( 2*np.pi*self.frequency*t + self.theta )
        self.theta += 2*np.pi*self.frequency*n/self.sampleRate

        return out
    
    def setFrequency_Hz( self, frequency_Hz:float ) -> None:
        self.frequency = frequency_Hz

    def getFrequency_Hz( self ) -> float:
        return self.frequency 
