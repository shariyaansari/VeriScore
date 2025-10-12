// // src/contexts/VerificationContext.jsx
// import React, { createContext, useState, useEffect } from 'react';

// export const VerificationContext = createContext();

// export const VerificationProvider = ({ children }) => {
//   const [verifications, setVerifications] = useState([]);

//   // This function is called by AddressVerification.jsx
//   const addVerification = (newVerification) => {
//     // Adds the new result to the top of the list, keeping the last 5
//     setVerifications(prev => [newVerification, ...prev].slice(0, 5));
//   };
  
//   // We can also load initial data here if we want
//   useEffect(() => {
//     // Optional: fetch initial recent verifications when the app loads
//   }, []);

//   return (
//     <VerificationContext.Provider value={{ verifications, addVerification }}>
//       {children}
//     </VerificationContext.Provider>
//   );
// };
import React, { createContext, useState, useEffect } from 'react';

export const VerificationContext = createContext();

export const VerificationProvider = ({ children }) => {
  const [verifications, setVerifications] = useState([]);

  // This function will fetch the initial list of verifications when the app loads
  const loadInitialVerifications = async () => {
    try {
      const response = await fetch('http://127.0.0.1:5000/api/dashboard-stats');
      const data = await response.json();
      // We only care about the list here
      setVerifications(data.recent_verifications || []);
    } catch (error) {
      console.error("Failed to load initial verifications:", error);
    }
  };
  
  // Load the data once when the component first mounts
  useEffect(() => {
    loadInitialVerifications();
  }, []);

  // This function is called by the verification page to add a new item in real-time
  const addVerification = (newVerification) => {
    // Add the new item to the top of the list, keeping it to 5 items
    setVerifications(prev => [newVerification, ...prev].slice(0, 5));
  };

  return (
    <VerificationContext.Provider value={{ verifications, addVerification }}>
      {children}
    </VerificationContext.Provider>
  );
};