import React from "react";

type ResultCardProps = {
  testCase: string;
  result: string;
};

const ResultCard: React.FC<ResultCardProps> = ({ testCase, result }) => (
  <div className="border p-4 rounded-md shadow-md ">
    <h3 className="text-lg font-bold">{testCase}</h3>
    <p
      className={`mt-2 ${
        result === "Passed" ? "text-green-600" : "text-red-600"
      }`}
    >
      {result}
    </p>
  </div>
);

export default ResultCard;
