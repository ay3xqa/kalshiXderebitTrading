import React, {useState, useEffect} from "react";
import axios from "axios";
import "../CSS/Event.css"; // Make sure to link your CSS

const EventContainer = (props) => {
  // Format target price as currency with commas
  const formattedTargetPrice = `$${props.target_price.toLocaleString()}`;

  // Format yes_price and no_price with two decimal places
  const formattedYesPrice = `${(props.yes_price).toFixed(0)}¢`;
  const formattedNoPrice = `${(props.no_price).toFixed(0)}¢`;

  const yesDiff = props.yes_prob !== null ? props.yes_prob - props.yes_price: 0;
  const noDiff = props.no_prob !== null ? props.no_prob - props.no_price: 0;

  // Determine the class based on the probability difference
  const yesContainerClass = yesDiff >= 5 ? "green-border" : "red-border";
  const noContainerClass = noDiff >= 5 ? "green-border" : "red-border";

  return (
    <div className="EventContainer">
      <span className="target-price">{formattedTargetPrice}</span>
      <div className={`price-prob-container ${yesContainerClass}`}>
        <span className="yes-price">{formattedYesPrice}</span>
        <span className="yes-prob">{props.yes_prob !== null ? `${props.yes_prob}%` : "Loading..."}</span>
      </div>
      <div className={`price-prob-container ${noContainerClass}`}>
        <span className="no-price">{formattedNoPrice}</span>
        <span className="no-prob">{props.no_prob !== null ? `${props.no_prob}%` : "Loading..."}</span>
      </div>
    </div>
  );
};

export default EventContainer;
