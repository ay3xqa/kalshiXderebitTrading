import React, {useState} from 'react';
import EventContainer from './Event.js';
// import mockData from "../mock-kalshi-data.json";
import "../CSS/Market.css";

export default function Market({kalshiData}) {
    const [isExpanded, setIsExpanded] = useState(true);
    // Toggle function to expand/collapse the market
    const toggleMarket = () => {
        setIsExpanded(!isExpanded);
    };

    const events = kalshiData["market_data"].map((event, index) => {
        return (
            <EventContainer
                key = {index}
                yes_price = {event.yes_price}
                no_price = {event.no_price}
                target_price = {event.target_price}
            />
        );
    });
    return (
         <div className="market-container">
            <div className="market-title" onClick={toggleMarket}>
                {kalshiData["market_title"]}
                <span className="toggle-icon">{isExpanded ? "▼" : "►"}</span>
            </div>
            {isExpanded && (
                <div className="event-list">
                    {events}
                </div>
            )}
        </div>
    )
}
