const BACKEND_URL = import.meta.env.VITE_BACKEND_URL || 'http://localhost:8000';

export const detectForgery = async (file) => {
  const formData = new FormData();
  formData.append('file', file);

  const response = await fetch(`${BACKEND_URL}/detect`, {
    method: 'POST',
    body: formData,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    throw new Error(errorData.detail || 'Failed to analyze image. Ensure backend is running.');
  }

  return response.json();
};

export const downloadReport = async (resultData) => {
  const response = await fetch(`${BACKEND_URL}/report`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      result_data: resultData
    }),
  });

  if (!response.ok) {
    throw new Error('Failed to download report.');
  }

  const blob = await response.blob();
  const url = window.URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = 'Forensic_Report.pdf';
  document.body.appendChild(a);
  a.click();
  a.remove();
  window.URL.revokeObjectURL(url);
};

export const explainWithAI = async (resultData, apiKey, provider) => {
  const prompt = `You are an expert digital forensics AI. Analyze this image forgery detection result JSON.
Explain the findings clearly, what was detected, where it was found (mentioning heatmap/keypoints), why it matters, and whether this indicates intentional tampering or legal document forgery.

Result JSON:
${JSON.stringify(resultData, null, 2)}`;

  if (provider === 'GPT-4' || provider === 'OpenAI') {
    const res = await fetch('https://api.openai.com/v1/chat/completions', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'Authorization': `Bearer ${apiKey}`
      },
      body: JSON.stringify({
        model: 'gpt-4o-mini',
        max_tokens: 600,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    if (!res.ok) throw new Error('OpenAI API request failed. Check API Key.');
    const data = await res.json();
    return data.choices[0].message.content;
  } else if (provider === 'Claude' || provider === 'Anthropic') {
    const res = await fetch('https://api.anthropic.com/v1/messages', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        'x-api-key': apiKey,
        'anthropic-version': '2023-06-01',
        'anthropic-dangerously-allow-browser': 'true'
      },
      body: JSON.stringify({
        model: 'claude-3-haiku-20240307',
        max_tokens: 600,
        messages: [{ role: 'user', content: prompt }]
      })
    });
    if (!res.ok) throw new Error('Anthropic API request failed. Check API Key.');
    const data = await res.json();
    return data.content[0].text;
  } else if (provider === 'Gemini' || provider === 'Google') {
    const res = await fetch(`https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key=${apiKey}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        contents: [{ parts: [{ text: prompt }] }]
      })
    });
    if (!res.ok) throw new Error('Gemini API request failed. Check API Key.');
    const data = await res.json();
    return data.candidates[0].content.parts[0].text;
  } else {
    throw new Error('Unsupported AI Provider');
  }
};
