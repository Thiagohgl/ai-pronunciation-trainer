import React, { useState, useRef } from 'react';
import {
  Box,
  Button,
  CircularProgress,
  Typography,
  Paper,
  Stack,
} from '@mui/material';
import { red, green } from '@mui/material/colors';
import { Mic, Stop } from '@mui/icons-material';

const App: React.FC = () => {
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [recording, setRecording] = useState(false);
  const mediaRecorderRef = useRef<MediaRecorder | null>(null);
  const audioChunks = useRef<Blob[]>([]);
  const audioStreamRef = useRef<MediaStream | null>(null);

  const prompts = [
    "I usually wake up at seven in the morning.",
    "She likes to listen to music while studying English.",
    "Can you tell me more about your hometown?",
    "I often go for a walk in the evening.",
    "He is watching a movie with his little brother now.",
    "They are planning to travel to Japan next year.",
    "I really enjoy eating noodles on rainy days.",
    "We have a big test at school this Friday.",
    "My favorite hobby is reading books before bedtime.",
    "The cat is sleeping under the table right now.",
    "I want to become a good English speaker someday.",
    "She goes to the library every Saturday morning.",
    "Let’s cook something delicious for dinner tonight, okay?",
    "He always drinks coffee before starting his workday.",
    "Do you want to join us for lunch today?",
    "I forgot my umbrella at home this morning.",
    "We are learning how to speak English fluently.",
    "Please give me a moment to think about it.",
    "I saw a beautiful bird flying across the sky.",
    "They play soccer together every Sunday afternoon."
  ];
  const [titleText, setTitleText] = useState('');
  const titleTextRef = useRef("");

  const startRecording = async () => {
    setResponse(null);
    setLoading(false);
    const randomPrompt = prompts[Math.floor(Math.random() * prompts.length)];
    setTitleText(randomPrompt);
    titleTextRef.current = randomPrompt;

    try {
      const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
      audioStreamRef.current = stream;
      const mediaRecorder = new MediaRecorder(stream);
      mediaRecorderRef.current = mediaRecorder;
      audioChunks.current = [];

      mediaRecorder.ondataavailable = (event) => {
        if (event.data.size > 0) {
          audioChunks.current.push(event.data);
        }
      };

      mediaRecorder.onstop = handleRecordingStop;

      mediaRecorder.start();
      setRecording(true);
    } catch (err) {
      console.error('Microphone access denied or not available:', err);
    }
  };

  const stopRecording = () => {
    mediaRecorderRef.current?.stop();
    audioStreamRef.current?.getTracks().forEach((track) => track.stop());
    setRecording(false);
  };

  const handleRecordingStop = async () => {
    const blob = new Blob(audioChunks.current, { type: 'audio/webm' });
    const arrayBuffer = await blob.arrayBuffer();
    const audioContext = new AudioContext();
    const audioBuffer = await audioContext.decodeAudioData(arrayBuffer);

    const wavBuffer = encodeWAV(audioBuffer);
    const base64Wav = bufferToBase64(wavBuffer);

    console.log("titleText" + titleTextRef.current)
    const payload = {
      title: titleTextRef.current,
      base64Audio: `data:audio/wav;base64,${base64Wav}`,
      language: 'en',
    };

    setLoading(true);
    try {
      const res = await fetch('http://localhost:8080/GetAccuracyFromRecordedAudio', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload),
      });

      const data = await res.json();
      setResponse({ status: res.status, data });
    } catch (error) {
      console.error('Error sending audio:', error);
    } finally {
      setLoading(false);
    }
  };

  const encodeWAV = (audioBuffer: AudioBuffer): ArrayBuffer => {
    const numChannels = audioBuffer.numberOfChannels;
    const sampleRate = audioBuffer.sampleRate;
    const format = 1;
    const bitsPerSample = 16;
    const samples = audioBuffer.getChannelData(0);
    const buffer = new ArrayBuffer(44 + samples.length * 2);
    const view = new DataView(buffer);

    function writeString(offset: number, str: string) {
      for (let i = 0; i < str.length; i++) {
        view.setUint8(offset + i, str.charCodeAt(i));
      }
    }

    function floatTo16BitPCM(output: DataView, offset: number, input: Float32Array) {
      for (let i = 0; i < input.length; i++, offset += 2) {
        const s = Math.max(-1, Math.min(1, input[i]));
        output.setInt16(offset, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
      }
    }

    writeString(0, 'RIFF');
    view.setUint32(4, 36 + samples.length * 2, true);
    writeString(8, 'WAVE');
    writeString(12, 'fmt ');
    view.setUint32(16, 16, true);
    view.setUint16(20, format, true);
    view.setUint16(22, numChannels, true);
    view.setUint32(24, sampleRate, true);
    view.setUint32(28, sampleRate * numChannels * bitsPerSample / 8, true);
    view.setUint16(32, numChannels * bitsPerSample / 8, true);
    view.setUint16(34, bitsPerSample, true);
    writeString(36, 'data');
    view.setUint32(40, samples.length * 2, true);
    floatTo16BitPCM(view, 44, samples);

    return buffer;
  };

  const bufferToBase64 = (buffer: ArrayBuffer): string => {
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
      binary += String.fromCharCode(bytes[i]);
    }
    return btoa(binary);
  };

  const renderColoredTranscript = () => {
    const text = response.data.real_transcripts;
    const correctness = response.data.is_letter_correct_all_words.replace(/\s/g, '');
    return (
      <Typography sx={{ wordBreak: 'break-word', fontSize: '1.2rem' }}>
        {text.split('').map((char: string, i: number) => (
          <span
            key={i}
            style={{
              color: correctness[i] === '1' ? green[600] : red[600],
              fontWeight: 'bold',
            }}
          >
            {char}
          </span>
        ))}
      </Typography>
    );
  };

  return (
    <Box
      display="flex"
      justifyContent="center"
      alignItems="center"
      minHeight="100vh"
      bgcolor="#f5f5f5"
    >
      <Paper elevation={4} sx={{ p: 4, maxWidth: 600, width: '100%', textAlign: 'center' }}>
        <Typography variant="h5" gutterBottom>
          Pronunciation Analyzer
        </Typography>

        <Box mt={3} mb={3}>
          {titleText && (
            <Typography variant="h6" sx={{ mb: 2 }}>
              <em>"{titleText}"</em>
            </Typography>
          )}
          <Button
            onClick={recording ? stopRecording : startRecording}
            variant="contained"
            color={recording ? 'error' : 'primary'}
            size="large"
            sx={{
              borderRadius: '50%',
              width: 80,
              height: 80,
              minWidth: 0,
              boxShadow: 3,
              transition: 'all 0.3s ease-in-out',
              '&:hover': {
                boxShadow: 6,
                transform: 'scale(1.05)',
              },
            }}
          >
            {recording ? <Stop fontSize="large" /> : <Mic fontSize="large" />}
          </Button>
        </Box>

        {loading && <CircularProgress />}

        {response && (
          <Box mt={4}>
            <Typography variant="subtitle1" gutterBottom>
              <strong>Status Code:</strong> {response.status}
            </Typography>

            <Typography variant="subtitle2" gutterBottom>
              <strong>Real Transcript:</strong> {response.data.real_transcript}
            </Typography>
            <Typography variant="subtitle2" gutterBottom>
              <strong>IPA:</strong> {response.data.ipa_transcript}
            </Typography>
            <Typography variant="subtitle2" gutterBottom>
              <strong>Accuracy:</strong> {response.data.pronunciation_accuracy}%
            </Typography>

            <Box mt={2}>
              <Typography variant="subtitle2" gutterBottom>
                <strong>Per-letter Accuracy:</strong>
              </Typography>
              <Paper sx={{ p: 2, backgroundColor: '#fff' }} variant="outlined">
                {renderColoredTranscript()}
              </Paper>
            </Box>
          </Box>
        )}
      </Paper>
    </Box>
  );
};

export default App;
