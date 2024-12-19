import React, {useState} from 'react';
import "../CSS/Calculator.css";


export default function Hero() {

const [contractType, setContractType] = useState("YES");
  const [targetPrice, setTargetPrice] = useState(150000); // Default slider value in the middle
  const [lowerBound, setLowerBound] = useState(50000); // Default lower bound for range
  const [upperBound, setUpperBound] = useState(100000); // Default upper bound for range
  const [mode, setMode] = useState("Target"); // Either "Target" or "Range"

  const [result, setResult] = useState(null);

  
  // Function to handle form submission
  const handleSubmit = async (e) => {
    e.preventDefault();
    let url;
    if (mode === "Target") {
      // Construct the URL for target price
      url = `http://127.0.0.1:5000/get_probability_target?contract_type=${contractType.toLowerCase()}&target_price=${targetPrice}`;
    } else {
      // Construct the URL for range (lower and upper bounds)
      url = `http://127.0.0.1:5000/get_probability_range?contract_type=${contractType.toLowerCase()}&lower_bound=${lowerBound}&upper_bound=${upperBound}`;
    }

    // Send a GET request
    try {
      const response = await fetch(url, {
        method: "GET",
      });

      if (response.ok) {
        const resultData = await response.json(); // Assuming the response is JSON
        setResult(resultData); // Store the result in state
      } else {
        console.error("Error fetching the data.");
      }
    } catch (error) {
      console.error("Error:", error);
    }
  };

  //handle live time input changes
  const handleInputChange = (e) => {
    const value = e.target.value;
    // Make sure the value is within the slider range (0 - 300000)
    if (value >= 0 && value <= 300000) {
      setTargetPrice(value);
    }
  };
  const handleLowerBoundChange = (e) => setLowerBound(e.target.value);
  const handleUpperBoundChange = (e) => setUpperBound(e.target.value);

  return (
    <div className="contract-form">
    <h2>Enter Contract Paramaters</h2>
    <div className="toggle-buttons">
        <button
          className={mode === "Target" ? "active" : ""}
          onClick={() => {
            setMode("Target")
            setResult(null)
          }}
        >
          Target
        </button>
        <button
          className={mode === "Range" ? "active" : ""}
          onClick={() => {
            setMode("Range")
            setResult(null)
          }}
        >
          Range
        </button>
    </div>

    <div className="toggle-buttons">
      <button
        className={contractType === "YES" ? "active" : ""}
        onClick={() => setContractType("YES")}
      >
        YES
      </button>
      <button
        className={contractType === "NO" ? "active" : ""}
        onClick={() => setContractType("NO")}
      >
        NO
      </button>
    </div>

    {mode === "Target" && (
        <div className="slider-container">
          <label>Target Price: {targetPrice}</label>
          <input
            type="range"
            min="0"
            max="300000"
            value={targetPrice}
            onChange={(e) => setTargetPrice(e.target.value)}
          />
          <input
            type="number"
            min="0"
            max="300000"
            value={targetPrice}
            onChange={handleInputChange}
            className="price-input"
          />
        </div>
      )}


      {mode === "Range" && (
        <div className="range-inputs">
          <div className="range-field">
            <label>Lower Bound:</label>
            <input
              type="number"
              min="0"
              max="300000"
              value={lowerBound}
              onChange={handleLowerBoundChange}
              className="price-input"
            />
          </div>
          <div className="range-field">
            <label>Upper Bound:</label>
            <input
              type="number"
              min="0"
              max="300000"
              value={upperBound}
              onChange={handleUpperBoundChange}
              className="price-input"
            />
          </div>
        </div>
      )}

    <button className="submit-button" onClick={handleSubmit}>
      Submit
    </button>

    {result && (
        <div className="result">
          <h3>Response from server:</h3>
          <p>Expected Probability: {result.data}%</p>
        </div>
      )}
  </div>
  )
}
