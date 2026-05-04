import React, { useState } from 'react';

export const IncidentDashboard = () => {
  const [query, setQuery] = useState('');
  const [results, setResults] = useState([]);
  const [loading, setLoading] = useState(false);

  const handleSearch = async () => {
    setLoading(true);
    // AI Challenge: Implement the fetch call to /search and handle the confidence-based coloring
    // as defined in .cursor/rules.md
    setLoading(false);
  };

  return (
    <div className="max-w-4xl mx-auto p-8 font-sans">
      <header className="mb-10">
        <h1 className="text-3xl font-bold text-slate-900">The Watchtower</h1>
        <p className="text-slate-500">Incident Intelligence & RAG Retrieval</p>
      </header>

      <div className="flex gap-2 mb-8">
        <input 
          type="text" 
          value={query}
          onChange={(e) => setQuery(e.target.value)}
          placeholder="Ask about past incidents (e.g., 'Database connection timeout in production')"
          className="flex-1 px-4 py-2 border rounded-md focus:outline-none focus:ring-2 focus:ring-blue-500"
        />
        <button 
          onClick={handleSearch}
          className="px-6 py-2 bg-blue-600 text-white rounded-md hover:bg-blue-700 transition-colors"
        >
          {loading ? 'Analyzing...' : 'Search'}
        </button>
      </div>

      <div className="space-y-4">
        {/* AI will generate the search results here using the Confidence Score rules */}
        <div className="p-4 border rounded-lg bg-slate-50 border-dashed border-slate-300 text-center text-slate-400">
          No active search. Enter a query to retrieve historical context.
        </div>
      </div>
    </div>
  );
};
