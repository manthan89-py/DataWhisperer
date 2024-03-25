import React, { useState } from "react";
import "./App.css";

export default function App() {
  const [result, setResult] = useState();
  const [question, setQuestion] = useState();
  const [file, setFile] = useState();
  const [loading, setLoading] = useState(false);

  const handleQuestionChange = (event: any) => {
    setQuestion(event.target.value);
  };

  const handleFileChange = (event: any) => {
    setFile(event.target.files[0]);
  };

  const handleSubmit = async (event: any) => {
    event.preventDefault();
    setLoading(true); // Set loading to true

    const formData = new FormData();

    if (file) {
      formData.append("uploaded_file", file);
    }

    // Call /createdb endpoint to create the database
    try {
      const createDbResponse = await fetch("http://127.0.0.1:8000/createdb", {
        method: "POST",
        body: formData,
      });
      if (!createDbResponse.ok) {
        throw new Error("Failed to create database");
      }

      // Once the database is created, call /predict endpoint with the question
      if (question) {
        let questionformData = { question: question };
        const predictResponse = await fetch("http://127.0.0.1:8000/predict", {
          method: "POST",
          headers: { "Content-Type": "application/json" },
          body: JSON.stringify(questionformData),
        });
        if (!predictResponse.ok) {
          throw new Error("Failed to get prediction");
        }
        const data = await predictResponse.json();
        setResult(data.result);
      }
    } catch (error) {
      console.error("Error", error);
    } finally {
      setLoading(false); // Set loading back to false
    }
  };

  return (
    <div className="chatbot-container">
      <h1 className="chatbot-title">File Based Chatbot</h1>
      <div className="appBlock">
        <form onSubmit={handleSubmit} className="form">
          <label className="questionLabel" htmlFor="question">
            Question:
          </label>
          <input
            className="questionInput"
            id="question"
            type="text"
            value={question}
            onChange={handleQuestionChange}
            placeholder="Ask your question here"
          />

          <br></br>
          <label className="fileLabel" htmlFor="file">
            Upload file:
          </label>

          <input
            type="file"
            id="file"
            name="file"
            accept=".txt,.md,.docx,,.pdf"
            onChange={handleFileChange}
            className="fileInput"
          />
          <br></br>
          <button
            className="submitBtn"
            type="submit"
            disabled={!file || !question || loading} // Disable button when loading
          >
            {loading ? "Submitting..." : "Submit"}
          </button>
        </form>
        {loading ? (
          <p className="loadingOutput">Loading...</p>
        ) : (
          <p className="answer-card">Answer: {result}</p>
        )}
      </div>
    </div>
  );
}
