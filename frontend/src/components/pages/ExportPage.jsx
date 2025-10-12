// // import React from 'react';
// // import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card';
// // import { Button } from '../ui/button';
// // import { Download, FileSpreadsheet } from 'lucide-react';

// // const ExportPage = () => {
// //   return (
// //     <div className="max-w-xl mx-auto space-y-10 px-4 pt-10">
// //       <div>
// //         <h1 className="text-3xl font-extrabold mb-1 tracking-tight">
// //           Export Verification Data
// //         </h1>
// //         <p className="text-muted-foreground text-base">
// //           Download all historical verification data as a single CSV file.
// //         </p>
// //       </div>
// //       <Card className="shadow-xl rounded-xl border hover:shadow-2xl transition p-2">
// //         <CardHeader>
// //           <CardTitle className="flex items-center gap-2">
// //             <FileSpreadsheet className="h-5 w-5" />
// //             Download Report
// //           </CardTitle>
// //           <CardDescription>
// //             The generated CSV file can be opened in Excel, Google Sheets, or any other spreadsheet software for analysis.
// //           </CardDescription>
// //         </CardHeader>
// //         <CardContent>
// //           <a href="http://127.0.0.1:5000/api/export-csv" download>
// //             <Button
// //               className="w-full font-semibold py-2 text-base flex items-center justify-center gap-2"
// //               size="lg"
// //             >
// //               <Download className="h-4 w-4" />
// //               Download All Verifications as CSV
// //             </Button>
// //           </a>
// //         </CardContent>
// //       </Card>
// //     </div>
// //   );
// // };

// // export default ExportPage;


// import React, { useState } from 'react';
// import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card';
// import { Button } from '../ui/button';
// import { Upload, FileSpreadsheet, RefreshCw, Download } from 'lucide-react';
// import Papa from 'papaparse';

// const ExportPage = () => {
//   const [file, setFile] = useState(null);
//   const [parsedData, setParsedData] = useState(null);
//   const [processing, setProcessing] = useState(false);

//   const handleFileChange = (event) => {
//     const selected = event.target.files[0];
//     setFile(selected);
//     setParsedData(null);
//     if (selected) {
//       setProcessing(true);
//       Papa.parse(selected, {
//         header: true,
//         complete: (results) => {
//           // Here you can run client-side processing on results.data
//           setParsedData(results.data);
//           setProcessing(false);
//         }
//       });
//     }
//   };

//   const handleDownload = () => {
//     if (!parsedData || !parsedData.length) return;
//     // Process the data here if you want (e.g., clean-up/transform)
//     const csv = Papa.unparse(parsedData);
//     const blob = new Blob([csv], { type: 'text/csv' });
//     const url = URL.createObjectURL(blob);
//     const link = document.createElement('a');
//     link.href = url;
//     link.download = "processed-verifications.csv";
//     document.body.appendChild(link);
//     link.click();
//     document.body.removeChild(link);
//     URL.revokeObjectURL(url);
//   };

//   return (
//     <div className="max-w-xl mx-auto space-y-10 px-4 pt-10">
//       <div>
//         <h1 className="text-3xl font-extrabold mb-1 tracking-tight">
//           Process or Export Verification Data
//         </h1>
//         <p className="text-muted-foreground text-base">
//           Select a CSV file, optionally review the data and download a processed/exported version—all without uploading to a server.
//         </p>
//       </div>
//       <Card className="shadow-xl rounded-xl border hover:shadow-2xl transition p-2">
//         <CardHeader>
//           <CardTitle className="flex items-center gap-2">
//             <FileSpreadsheet className="h-5 w-5" />
//             Upload CSV File
//           </CardTitle>
//           <CardDescription>
//             All client-side: no backend needed.<br/>
//             CSV must have appropriate columns for your use-case.
//           </CardDescription>
//         </CardHeader>
//         <CardContent className="space-y-6">
//           <input
//             type="file"
//             accept=".csv"
//             onChange={handleFileChange}
//             disabled={processing}
//             className="block w-full file:mr-4 file:py-2 file:px-4 file:border-0
//               file:text-sm file:font-semibold file:bg-accent file:text-primary"
//           />
//           {processing && (
//             <div className="flex items-center gap-2 text-muted-foreground">
//               <RefreshCw className="animate-spin h-5 w-5" />
//               Processing...
//             </div>
//           )}
//           {file && !processing && (
//             <div className="mt-2 px-4 py-2 bg-accent/40 rounded text-muted-foreground border text-sm">
//               <div className="font-mono">File selected: {file.name}</div>
//               {parsedData && (
//                 <div>
//                   <div className="mb-2">
//                     <span className="text-xs">
//                       Parsed <span className="font-bold">{parsedData.length}</span> rows.
//                     </span>
//                   </div>
//                   <div className="max-h-36 overflow-auto rounded border">
//                     <table className="text-xs w-full">
//                       <thead>
//                         <tr>
//                           {Object.keys(parsedData[0] || {}).map((header) => (
//                             <th key={header} className="px-2 py-1 border-b">{header}</th>
//                           ))}
//                         </tr>
//                       </thead>
//                       <tbody>
//                         {parsedData.slice(0, 5).map((row, i) => (
//                           <tr key={i}>
//                             {Object.values(row).map((cell, j) => (
//                               <td key={j} className="px-2 py-1 border-b">{cell}</td>
//                             ))}
//                           </tr>
//                         ))}
//                         {parsedData.length > 5 && (
//                           <tr>
//                             <td colSpan={Object.keys(parsedData[0]).length} className="text-center py-1">
//                               ...and {parsedData.length - 5} more rows
//                             </td>
//                           </tr>
//                         )}
//                       </tbody>
//                     </table>
//                   </div>
//                 </div>
//               )}
//             </div>
//           )}
//           <Button
//             className="w-full font-semibold py-2 text-base flex items-center justify-center gap-2"
//             size="lg"
//             onClick={handleDownload}
//             disabled={!parsedData || !parsedData.length}
//           >
//             <Download className="h-4 w-4" />
//             Download Processed CSV
//           </Button>
//         </CardContent>
//       </Card>
//     </div>
//   );
// };

// export default ExportPage;

import React, { useState } from 'react';
import { Card, CardHeader, CardTitle, CardDescription, CardContent } from '../ui/card';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Upload, Download, RefreshCw, FileSpreadsheet } from 'lucide-react';
import { toast } from 'sonner';
import Papa from 'papaparse';

const ExportPage = () => {
  const [file, setFile] = useState(null);
  const [processedData, setProcessedData] = useState(null);
  const [processing, setProcessing] = useState(false);

  const handleFileChange = (event) => {
    const selectedFile = event.target.files[0];
    if (selectedFile) {
      setFile(selectedFile);
      setProcessing(true);
      setProcessedData(null); // Clear previous results

      // Simulate backend processing by adding a score to each row
      Papa.parse(selectedFile, {
        header: true,
        skipEmptyLines: true,
        complete: (results) => {
          setTimeout(() => { // Add a small delay to simulate work
            const dataWithScores = results.data.map(row => {
              const score = Math.random();
              const status = score > 0.8 ? "verified" : score > 0.4 ? "suspicious" : "rejected";
              return {
                ...row,
                confidence_score: (score * 100).toFixed(0),
                status: status,
              };
            });
            setProcessedData(dataWithScores);
            setProcessing(false);
            toast.success(`Processed ${dataWithScores.length} records.`);
          }, 1000);
        }
      });
    }
  };

  const handleDownload = () => {
    if (!processedData) {
      toast.error("No data to download.");
      return;
    }
    const csv = Papa.unparse(processedData);
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement("a");
    const url = URL.createObjectURL(blob);
    link.setAttribute("href", url);
    link.setAttribute("download", "veriscore_processed_export.csv");
    link.style.visibility = 'hidden';
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="max-w-3xl mx-auto">
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Bulk Verification & Export</h1>
        <p className="text-muted-foreground">Upload a CSV, see the confidence scores, and download the enriched file.</p>
      </div>
      <Card>
        <CardHeader>
          <CardTitle className="flex items-center"><Upload className="mr-2 h-5 w-5" />Step 1: Upload CSV</CardTitle>
          <CardDescription>
            The CSV must have columns named <strong>company_name</strong> and <strong>address</strong>.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Input type="file" accept=".csv" onChange={handleFileChange} disabled={processing} />
        </CardContent>
      </Card>

      {(processing || processedData) && (
        <Card className="mt-8">
          <CardHeader>
            <CardTitle className="flex items-center"><FileSpreadsheet className="mr-2 h-5 w-5" />Step 2: Review & Download</CardTitle>
            <CardDescription>
              A confidence score and status have been added to your data.
            </CardDescription>
          </CardHeader>
          <CardContent>
            {processing && (
              <div className="flex items-center justify-center h-24 text-muted-foreground">
                <RefreshCw className="mr-2 h-5 w-5 animate-spin" />
                <span>Processing records...</span>
              </div>
            )}
            {processedData && (
              <div className="space-y-4">
                <div className="max-h-48 overflow-auto rounded-md border">
                    <table className="w-full text-sm">
                        <thead className="sticky top-0 bg-secondary">
                            <tr>
                                {Object.keys(processedData[0] || {}).map(header => <th key={header} className="p-2 text-left font-semibold">{header}</th>)}
                            </tr>
                        </thead>
                        <tbody>
                            {processedData.slice(0, 10).map((row, i) => (
                                <tr key={i} className="border-t">
                                    {Object.values(row).map((cell, j) => <td key={j} className="p-2 truncate">{cell}</td>)}
                                </tr>
                            ))}
                        </tbody>
                    </table>
                </div>
                {processedData.length > 10 && <p className="text-xs text-center text-muted-foreground">Showing first 10 of {processedData.length} rows.</p>}
                <Button onClick={handleDownload} className="w-full">
                  <Download className="mr-2 h-4 w-4" />
                  Download Processed CSV
                </Button>
              </div>
            )}
          </CardContent>
        </Card>
      )}
    </div>
  );
};

export default ExportPage;

