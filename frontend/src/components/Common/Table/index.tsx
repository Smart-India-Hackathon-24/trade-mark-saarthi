// type ApiData = {
//     [key: string]: { [key: string]: number | string } | undefined;
// };  

const TableComponent:React.FC<{apiData:any}>=({apiData})=>{
    
    const columns = Object.keys(apiData);

  const rows: Record<string, number | string>[] = [];
  const numberOfRows = apiData[columns[0]] ? Object.values(apiData[columns[0]]!).length : 0;

  for (let i = 0; i < numberOfRows; i++) {
    const row: Record<string, number | string> = {};
    columns.forEach((col) => {
      row[col] = apiData[col]?.[i] ?? "";
    });
    rows.push(row);
  }

    return( <>
     <div className="overflow-x-auto">
      <table className="min-w-full border border-gray-200 bg-white rounded-md shadow-md">
        <thead>
          <tr className="bg-gray-100 text-gray-800">
            {columns.map((col) => (
              <th
                key={col}
                className="px-4 py-2 text-left border-b border-gray-300 font-semibold"
              >
                {col}
              </th>
            ))}
          </tr>
        </thead>
        <tbody>
          {rows.map((row, index) => (
            <tr
              key={index}
              className={`${
                index % 2 === 0 ? "bg-gray-500" : "bg-gray-400"
              } hover:bg-gray-100`}
            >
              {columns.map((col) => (
                <td key={col} className="px-4 py-2 border-b border-gray-300 text-black">
                  {row[col]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
    </>)
}

export default TableComponent;

