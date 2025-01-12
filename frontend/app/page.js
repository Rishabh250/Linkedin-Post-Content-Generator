"use client";

import React, { useEffect, useRef, useState, useCallback } from "react";
import "quill/dist/quill.snow.css";
import { Save, Settings2, Share2 } from "lucide-react";

const formatResponse = (text) => {
  if (!text) return '';

  // Handle markdown-style formatting
  const markdownReplacements = {
    '\\*\\*(.*?)\\*\\*': '<strong>$1</strong>', // Bold
    '\\*(.*?)\\*': '<em>$1</em>', // Italic 
    '### (.*)': '<h3>$1</h3>', // H3
    '## (.*)': '<h2>$1</h2>', // H2
    '# (.*)': '<h1>$1</h1>', // H1
    '\n': '<br>'
  };

  let formattedText = text;
  Object.entries(markdownReplacements).forEach(([pattern, replacement]) => {
    formattedText = formattedText.replace(new RegExp(pattern, 'g'), replacement);
  });

  // Split and process paragraphs
  const paragraphs = formattedText.split('<br><br>').filter(p => p.trim());
  
  return paragraphs.map(paragraph => {
    // Handle lists
    if (paragraph.includes('<br>-') || paragraph.includes('<br>*') || /\d+\./.test(paragraph)) {
      const [intro, ...points] = paragraph.split('<br>');
      
      const introHtml = intro.trim() ? `<p>${intro.trim()}</p>` : '';
      
      const listItems = points
        .filter(point => point.trim())
        .map(point => `<li>${point.replace(/^[-*]\d*\.\s*/, '').trim()}</li>`)
        .join('');

      if (!listItems) return introHtml;

      const listType = /\d+\./.test(points[0]) ? 'ol' : 'ul';
      return `${introHtml}<${listType}>${listItems}</${listType}>`;
    }
    
    // Handle hashtags and regular paragraphs
    return paragraph.trim() ? `<p>${paragraph.trim()}</p>` : '';
  }).join('');
};

const TOOLBAR_OPTIONS = [
  ["bold", "italic", "underline", "strike"],
  [{ header: [1, 2, 3, false] }],
  [{ list: "ordered" }, { list: "bullet" }],
  [{ align: [] }],
  ["link"],
  ["clean"],
];

const AUDIENCE_OPTIONS = [
  { value: "marketing_professionals", label: "Marketing Professionals" },
  { value: "business_leaders", label: "Business Leaders" },
  { value: "tech_professionals", label: "Tech Professionals" },
  { value: "entrepreneurs", label: "Entrepreneurs" },
  { value: "general", label: "General Professional Network" }
];

const TONE_OPTIONS = [
  { value: "professional", label: "Professional" },
  { value: "casual", label: "Casual" },
  { value: "enthusiastic", label: "Enthusiastic" },
  { value: "authoritative", label: "Authoritative" }
];

const Home = () => {
  const quillRef = useRef(null);
  const editorRef = useRef(null);
  const [content, setContent] = useState("");
  const [topic, setTopic] = useState("");
  const [tone, setTone] = useState("");
  const [audience, setAudience] = useState("");
  const [isLoading, setIsLoading] = useState(false);

  const initializeQuill = useCallback(() => {
    if (typeof window !== 'undefined' && !quillRef.current && editorRef.current) {
      import('quill').then((Quill) => {
        quillRef.current = new Quill.default(editorRef.current, {
          theme: "snow",
          placeholder: "Write your post here...",
          modules: { toolbar: TOOLBAR_OPTIONS },
        });

        quillRef.current.on("text-change", () => {
          setContent(quillRef.current.root.innerHTML);
        });
      });
    }
  }, []);

  useEffect(() => {
    initializeQuill();
    return () => {
      if (quillRef.current) {
        quillRef.current.off("text-change");
        quillRef.current = null;
      }
    };
  }, [initializeQuill]);

  const handleSave = useCallback(() => {
    if (quillRef.current) {
      console.log("Saved content:", content);
    }
  }, [content]);

  const handleGenerate = useCallback(async () => {
    if (!topic || !tone || !audience) {
      alert("Please fill in all fields");
      return;
    }

    setIsLoading(true);
    try {
      const response = await fetch('http://localhost:8000/generate-post', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ topic, tone, audience })
      });

      const data = await response.json();
      if (data.status === 'success' && quillRef.current) {
        quillRef.current.root.innerHTML = formatResponse(data.post);
      } else {
        alert('Failed to generate post: ' + data.message);
      }
    } catch (error) {
      alert('Error generating post: ' + error.message);
    } finally {
      setIsLoading(false);
    }
  }, [topic, tone, audience]);

  const renderSelect = useCallback(({ value, onChange, options, label }) => (
    <div>
      <label className="block text-sm font-medium text-gray-700 mb-1">
        {label}
      </label>
      <select
        value={value}
        onChange={(e) => onChange(e.target.value)}
        className="w-full p-2 border rounded-md focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
      >
        <option value="">Select {label.toLowerCase()}</option>
        {options.map(({ value, label }) => (
          <option key={value} value={value}>{label}</option>
        ))}
      </select>
    </div>
  ), []);

  return (
  <div className="min-h-screen bg-gradient-to-br from-gray-50 to-gray-100">
  <main className="mx-auto px-4 py-8">
    <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
      <div className="bg-gradient-to-r from-blue-600 to-blue-800 p-8">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-2xl font-bold text-white">LinkedIn Post Generator</h2>
            <p className="mt-2 text-blue-100">Create engaging content for your professional network</p>
          </div>
          <Settings2 className="text-white h-6 w-6 opacity-75 hover:opacity-100 cursor-pointer transition-opacity" />
        </div>
      </div>
      
      <div className="p-8 grid grid-cols-[320px_1fr] gap-8">
        <div className="space-y-6">
          <div className="bg-gray-50 p-6 rounded-xl space-y-6">
            <div className="space-y-2">
              <label className="block text-sm font-medium text-gray-700">Topic</label>
              <input
                type="text"
                value={topic}
                onChange={(e) => setTopic(e.target.value)}
                className="w-full p-3 border rounded-lg shadow-sm focus:ring-2 focus:ring-blue-500 focus:border-blue-500 transition-all duration-200"
                placeholder="e.g., AI in Marketing"
              />
            </div>
            {renderSelect({
              value: tone,
              onChange: setTone,
              options: TONE_OPTIONS,
              label: "Tone"
            })}
            {renderSelect({
              value: audience,
              onChange: setAudience,
              options: AUDIENCE_OPTIONS,
              label: "Target Audience"
            })}
          </div>
          
          <button
            className="w-full py-4 px-6 bg-blue-600 text-white rounded-xl hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 disabled:bg-gray-400 transition-all duration-200 shadow-lg hover:shadow-xl flex items-center justify-center space-x-2"
            onClick={handleGenerate}
            disabled={isLoading}
          >
            {isLoading ? (
              <span className="flex items-center justify-center">
                <svg className="animate-spin -ml-1 mr-3 h-5 w-5 text-white" xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24">
                  <circle className="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4"></circle>
                  <path className="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
                </svg>
                <span>Generating...</span>
              </span>
            ) : (
              <>
                <Share2 className="h-5 w-5" />
                <span>Generate Post Content</span>
              </>
            )}
          </button>
        </div>

        <div className="border rounded-xl shadow-sm bg-white overflow-hidden h-[900px]">
          <div ref={editorRef} className="h-[600px] overflow-y-auto" />
          <div className="border-t p-4 flex justify-between items-center bg-gray-50">
            <span className="text-sm text-gray-600 flex items-center space-x-2">
              <span>{content.replace(/<[^>]*>/g, "").length} characters</span>
              <span className="text-gray-300">|</span>
              <span className="text-blue-600 hover:text-blue-700 cursor-pointer">View Preview</span>
            </span>
            <button
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 transition-all duration-200 flex items-center space-x-2"
              onClick={handleSave}
            >
              <Save className="h-4 w-4" />
              <span>Save Post</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </main>
  </div>
  );
};

export default Home;