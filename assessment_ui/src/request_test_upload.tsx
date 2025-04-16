import React, { useState } from 'react';

const App: React.FC = () => {
  const [response, setResponse] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const handleFileChange = async (event: React.ChangeEvent<HTMLInputElement>) => {
    const file = event.target.files?.[0];
    if (!file) return;

    setLoading(true);

    try {
      const reader = new FileReader();
      reader.onloadend = async () => {
        const base64Audio = reader.result as string;

        const payload = {
          title: 'This problem is really complicated.',
          base64Audio: base64Audio,
          language: 'en'
        };

        const res = await fetch('http://localhost:8080/GetAccuracyFromRecordedAudio', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify(payload)
        });

        const data = await res.json();
        setResponse({ status: res.status, data });
      };

      reader.readAsDataURL(file); // Automatically creates data URI like "data:audio/wav;base64,..."
    } catch (error) {
      console.error('Error uploading file:', error);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div style={{ padding: '20px' }}>
      <h2>Upload Audio File</h2>
      <input type="file" accept="audio/wav" onChange={handleFileChange} />
      {loading && <p>Uploading and processing...</p>}
      {response && (
        <div>
          <h3>Status Code: {response.status}</h3>
          <h4>Response:</h4>
          <pre>{JSON.stringify(response.data, null, 2)}</pre>
        </div>
      )}
    </div>
  );
};

export default App;
