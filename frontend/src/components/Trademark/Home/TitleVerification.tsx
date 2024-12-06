"use client";
import Loader from "@/components/Common/Loader";
import axios from "axios";
import React, { useState } from 'react'

type TestCaseResult = {
    id: number;
    name: string;
    status: "Loading" | "Passed" | "Failed";
};

const TitleVerification = () => {
    const [title, setTitle] = useState("");
    const [englishText, setEnglishText] = useState('');
    const [translatedText, setTranslatedText] = useState('');
    const [isVerified, setIsVerified] = useState(false);
    const [results, setResults] = useState<{ testCase: string; result: string,message:string }[]>([]);
    const [testCases, setTestCases] = useState<TestCaseResult[]>([]);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState("");

    const apiEndpoints = [
        `${process.env.NEXT_PUBLIC_API_URL}/trademark/getdataontitle`,
        `${process.env.NEXT_PUBLIC_API_URL}/trademark/getdataontitle`,

    ];

    // Simulate translation (Replace with actual API)
    const translateText = async (text: string) => {
        try {
            const translation = `Translated: ${text} (in Hindi)`; 
            setTranslatedText(translation);
        } catch (error) {
            console.error('Translation failed:', error);
            setTranslatedText('Translation error occurred.');
        }
    };

    const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
        const text = e.target.value;
        setEnglishText(text);
        translateText(text); 
        setIsVerified(false); 
    };

    const handleVerification = () => {
        if (englishText && translatedText) {
            setIsVerified(true);
        } else {
            alert('Please enter and translate the title first.');
        }
    };

    const fetchData = async (url: string, title: string, options?: { signal?: AbortSignal }) => {
        try {
            const response = await axios.get(`${url}?name=${title}`);
            return response?.data;
        } catch (error) {
            if (axios.isCancel(error)) {
                console.log('Request canceled:', error.message);
            }
            return { status: "Failed" };
        }
    };

    const executeApiCalls = async (apiEndpoints: string[], title: string, updatedTestCases: TestCaseResult[]) => {
        const abortControllers: AbortController[] = [];

        try {
            await Promise.all(
                apiEndpoints.map((endpoint, index) => {
                    const abortController = new AbortController();
                    abortControllers.push(abortController);

                    return (async () => {
                        const apiResult = await fetchData(endpoint, title, {
                            signal: abortController.signal
                        });
                        console.log("DDD",apiResult)
                        const status = apiResult?.result === true ? "Passed" : "Failed";
                        updatedTestCases[index].status = status;
                        
                        setResults(prev => [
                            ...prev,
                            { testCase: `Test Case ${index + 1}`, result: status, message: apiResult?.message }
                        ]);
                        setTestCases([...updatedTestCases]);

                        if (status === "Failed") {
                            abortControllers.forEach(controller => controller.abort());
                            throw new Error(`Test Case ${index + 1} failed`);
                        }
                    })();
                })
            );
        } catch (error) {
            console.error("Error during API execution:", error);
            setError("Verification failed. Please try again.");
        } finally {
            setLoading(false);
        }
    };

    const handleSubmit = async (e: React.FormEvent) => {
        e.preventDefault();
        setLoading(true);
        setError("");
        setResults([]);

        const initialTestCases: TestCaseResult[] = [
            { id: 0, name: "Test Case 1", status: "Loading" },
            { id: 1, name: "Test Case 2", status: "Loading" },
            { id: 2, name: "Test Case 3", status: "Loading" },
            { id: 3, name: "Test Case 4", status: "Loading" },
        ];

        setTestCases(initialTestCases);
        const updatedTestCases = [...initialTestCases];
        
        await executeApiCalls(apiEndpoints, title, updatedTestCases);
    };

    return (
        <>
            <h1 className="text-3xl font-bold text-center my-5">TradeMark Sarthi</h1>
            <div className="max-w-lg mx-auto mt-10 p-5 border rounded-lg">
                <h1 className="text-2xl font-bold mb-4">Title Verification</h1>
                <form onSubmit={handleSubmit} className="space-y-4">
                    <input
                        type="text"
                        value={title}
                        onChange={(e) => setTitle(e.target.value)}
                        placeholder="Enter title"
                        className="w-full p-3 border rounded-md focus:outline-none focus:ring focus:ring-blue-300 text-black"
                        required
                    />
                    <button
                        type="submit"
                        className="w-full p-3 bg-blue-800 text-white rounded-md hover:bg-blue-700"
                        disabled={loading}
                    >
                        {loading ? "Verifying..." : "Verify Title"}
                    </button>
                </form>
                {error && <p className="text-red-600 mt-4">{error}</p>}
                <div className="mt-6 space-y-4">
                    <div className="mt-6 space-y-4">
                        {results.map((testCase, index) => (
                            <div
                                key={index}
                                className="flex justify-between items-center p-4 border rounded-md shadow-md"
                            >
                                <div className="flex flex-col gap-2">
                                    <span className="font-semibold">{testCase.testCase}</span>
                                    <small>{testCase?.message}</small>
                                </div>
                                {testCase.result === "Loading" ? (
                                    <div><Loader/></div>
                                ) : (
                                    <span
                                        className={`font-bold ${
                                            testCase.result === "Passed"
                                                ? "text-green-600"
                                                : "text-red-600"
                                        }`}
                                    >
                                        {testCase.result}
                                    </span>
                                )}
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </>
    )
}

export default TitleVerification
