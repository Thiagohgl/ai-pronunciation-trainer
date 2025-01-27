import os


ALLOWED_ORIGIN = os.getenv('ALLOWED_ORIGIN', 'http://localhost:3000')
sample_rate_start = int(os.getenv('SAMPLE_RATE', 48000))
sample_rate_resample = 16000
