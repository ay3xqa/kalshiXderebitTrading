import React, {useState, useEffect} from "react";
import axios from "axios";
import "../CSS/Event.css"; // Make sure to link your CSS

const EventContainer = (props) => {
  // Format target price as currency with commas
  const formattedTargetPrice = `$${props.target_price.toLocaleString()}`;

  // Format yes_price and no_price with two decimal places
  const formattedYesPrice = `${(props.yes_price).toFixed(0)}¢`;
  const formattedNoPrice = `${(props.no_price).toFixed(0)}¢`;

  const [yesProbability, setYesProbability] = useState(null);
  const [noProbability, setNoProbability] = useState(null);

  const yesDiff = yesProbability !== null ? yesProbability - props.yes_price: 0;
  const noDiff = noProbability !== null ? noProbability - props.no_price: 0;

  // Determine the class based on the probability difference
  const yesContainerClass = yesDiff >= 5 ? "green-border" : "red-border";
  const noContainerClass = noDiff >= 5 ? "green-border" : "red-border";
  useEffect(() => {
    const fetchProbability = async () => {
      try {
        const yesResponse = await axios.get(
          `http://127.0.0.1:5000/get_probability_target?contract_type=yes&target_price=${props.target_price}`
        );
        const noResponse = await axios.get(
          `http://127.0.0.1:5000/get_probability_target?contract_type=no&target_price=${props.target_price}`
        );
        setYesProbability(yesResponse.data.data);
        setNoProbability(noResponse.data.data);
      } catch (error) {
        console.error("Error fetching probabilities:", error);
      }
    };

    fetchProbability();
  }, [props.target_price]); // Dependency: API call when target_price changes
  return (
    <div className="EventContainer">
      <span className="target-price">{formattedTargetPrice}</span>
      <div className={`price-prob-container ${yesContainerClass}`}>
        <span className="yes-price">{formattedYesPrice}</span>
        <span className="yes-prob">{yesProbability !== null ? `${yesProbability}%` : "Loading..."}</span>
      </div>
      <div className={`price-prob-container ${noContainerClass}`}>
        <span className="no-price">{formattedNoPrice}</span>
        <span className="no-prob">{noProbability !== null ? `${noProbability}%` : "Loading..."}</span>
      </div>
    </div>
  );
};

export default EventContainer;
