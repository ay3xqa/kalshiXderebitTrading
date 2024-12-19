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
                yes_prob = {event.yes_prob}
                no_prob = {event.no_prob}
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
                {kalshiData.market_data.length > 0 ? (
                    events
                ) : (
                    <div className="no-events-message">
                        No events available for this market.
                    </div>
                )}
            </div>
        )}
    </div>
    )
}
