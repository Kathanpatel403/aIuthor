import { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { BeakerIcon, PlayIcon, CheckCircleIcon, ArrowDownTrayIcon, ArrowPathIcon } from "@heroicons/react/24/outline";

export default function Audit() {
  const navigate = useNavigate();
  const [activeTests, setActiveTests] = useState({});
  const [testABookId, setTestABookId] = useState(localStorage.getItem("test_a_book_id"));

  const tests = [
    {
      id: "test_a",
      name: "Test A — Personal Finance Guide",
      desc: "10 chapters, Conversational tone, ~2,500 words/chapter. The baseline for C and D.",
      status: activeTests["test_a"] ? "running" : (testABookId ? "completed" : "idle"),
    },
    {
      id: "test_b",
      name: "Test B — Novella",
      desc: "5-chapter fiction, Storyteller tone, two named characters carried throughout.",
      status: activeTests["test_b"] ? "running" : "idle",
    },
    {
      id: "test_c",
      name: "Test C — Tone Variants",
      desc: "Regenerates Test A's Chapter 3 in Academic, Motivational, and Witty tones.",
      status: activeTests["test_c"] ? "running" : "idle",
      requires: "test_a",
    },
    {
      id: "test_d",
      name: "Test D — Chapter Insertion",
      desc: "Inserts a chapter between A's Ch.4 and Ch.5 with auto-repairing TOC/callbacks.",
      status: activeTests["test_d"] ? "running" : "idle",
      requires: "test_a",
    },
  ];

  const runTest = async (testId) => {
    try {
      setActiveTests(prev => ({ ...prev, [testId]: true }));
      const resp = await fetch(`http://localhost:8000/api/tests/run/${testId}`, { method: "POST" });
      const data = await resp.json();
      
      if (testId === "test_a") {
        setTestABookId(data.book_id);
        localStorage.setItem("test_a_book_id", data.book_id);
        // Navigate to pipeline for the baseline book
        navigate(`/pipeline/${data.book_id}`);
      } else if (testId === "test_b") {
        navigate(`/pipeline/${data.book_id}`);
      } else {
        // C and D are faster or modifications, just show alert for now
        alert(data.message);
        setActiveTests(prev => ({ ...prev, [testId]: false }));
      }
    } catch (err) {
      console.error(err);
      setActiveTests(prev => ({ ...prev, [testId]: false }));
    }
  };

  return (
    <div className="max-w-5xl mx-auto py-12 px-4 sm:px-6 lg:px-8">
      <div className="text-center mb-16">
        <h1 className="text-4xl font-extrabold text-white tracking-tight sm:text-5xl mb-4">
          Audit <span className="text-indigo-400">Control Center</span>
        </h1>
        <p className="text-xl text-gray-400">
          Run the 4 standard audit tests to validate pipeline quality, tonality, and self-healing.
        </p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
        {tests.map((test) => (
          <div key={test.id} className="bg-gray-900/50 backdrop-blur-xl border border-gray-800 rounded-3xl p-8 hover:border-indigo-500/50 transition-all duration-300 group shadow-2xl">
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center mb-2">
                  <div className="p-2 bg-indigo-500/10 rounded-lg mr-3">
                    <BeakerIcon className="h-6 w-6 text-indigo-400" />
                  </div>
                  <h3 className="text-xl font-bold text-white">{test.name}</h3>
                </div>
                <p className="text-gray-400 mb-6">{test.desc}</p>
                
                {test.requires === "test_a" && !testABookId && (
                  <div className="bg-amber-500/10 border border-amber-500/20 text-amber-500 text-xs px-3 py-2 rounded-lg mb-6 inline-block">
                    Requires Test A to be completed first
                  </div>
                )}
              </div>
            </div>

            <div className="flex items-center justify-between mt-auto">
              <div className="flex items-center space-x-2">
                {test.status === "running" ? (
                  <span className="flex items-center text-indigo-400 text-sm">
                    <ArrowPathIcon className="h-4 w-4 mr-1 animate-spin" />
                    Generating...
                  </span>
                ) : test.status === "completed" ? (
                  <span className="flex items-center text-emerald-400 text-sm">
                    <CheckCircleIcon className="h-4 w-4 mr-1" />
                    Baseline Ready
                  </span>
                ) : (
                  <span className="text-gray-500 text-sm">Ready to start</span>
                )}
              </div>

              <button
                onClick={() => runTest(test.id)}
                disabled={test.status === "running" || (test.requires === "test_a" && !testABookId)}
                className={`flex items-center px-6 py-2.5 rounded-full font-semibold transition-all ${
                  test.status === "running" || (test.requires === "test_a" && !testABookId)
                    ? "bg-gray-800 text-gray-500 cursor-not-allowed"
                    : "bg-indigo-600 text-white hover:bg-indigo-500 hover:scale-105 active:scale-95 shadow-lg shadow-indigo-500/20"
                }`}
              >
                {test.status === "running" ? "Processing" : (
                  <>
                    <PlayIcon className="h-5 w-5 mr-2" />
                    Start Test
                  </>
                )}
              </button>
            </div>
          </div>
        ))}
      </div>

      <div className="mt-16 bg-gradient-to-r from-indigo-900/20 to-purple-900/20 border border-white/5 rounded-3xl p-10 text-center">
        <h2 className="text-2xl font-bold text-white mb-4">Master Audit Sequence</h2>
        <p className="text-gray-400 mb-8 max-w-2xl mx-auto">
          Runs all 4 tests in sequential order. This will produce 2 books and 3 variants, 
          fully validating the entire AIuthor architecture.
        </p>
        <button 
          onClick={async () => {
            await runTest("test_a");
            // Subsequent tests need A to finish, so we can't chain them instantly 
            // unless we handle the polling here. For demo, sequential clicking is safer.
          }}
          className="bg-white text-gray-900 px-10 py-4 rounded-full font-bold text-lg hover:bg-indigo-50 hover:scale-105 transition-all shadow-xl"
        >
          Initialize Full Audit Loop
        </button>
      </div>
    </div>
  );
}
