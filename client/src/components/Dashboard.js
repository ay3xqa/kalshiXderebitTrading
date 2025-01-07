import React, { useState, useEffect } from 'react';
import Market from './Market.js';
import axios from 'axios';

export default function Dashboard() {
  const [kalshiData, setKalshiData] = useState(null); // Initialize with null
  const [loading, setLoading] = useState(true); // Track loading state

  const fetchKalshiJson = async () => {
    try {
      const response = await axios.get(
        `http://127.0.0.1:5001/get_all_kalshi_markets_json`
      );
      // console.log(response.data); // Log the data to inspect the structure
      setKalshiData(response.data.data.map((market, index) => {
        return (
            <Market
                key={index}
                kalshiData={market}
            />
        );
    })); // Adjust this based on actual data structure
    } catch (error) {
      console.error("Error fetching Kalshi Data:", error);
    } finally {
      setLoading(false); // End loading state
    }
  }

  useEffect(() => {
    fetchKalshiJson(); // Fetch data immediately on mount

    const intervalId = setInterval(() => {
      fetchKalshiJson(); // Fetch data every 30 seconds
      console.log("polled")
    }, 30000); // 30,000 milliseconds = 30 seconds

    // Cleanup function to clear the interval on component unmount
    return () => clearInterval(intervalId);
  }, []);

  // Conditional rendering to avoid rendering Market until data is available
  if (loading) {
    return <div>Loading...</div>;
  }

  if (!kalshiData) {
    return <div>No data available</div>;
  }

  return (
    <>
      <div>Dashboard</div>
      {/* Pass kalshiData to Market component only when data is available */}
      {/* <Market kalshiData={kalshiData} /> */}
      {kalshiData}
    </>
  );
}
