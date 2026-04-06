import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Train, Clock, MapPin, Calendar, CheckCircle2, CreditCard, Ticket, ArrowLeft, HeadphonesIcon } from 'lucide-react';
import AIAssistant from '../components/AIAssistant';
import SeatMap from '../components/SeatMap';
import './SupportTicket.css';

const SupportTicket = () => {
  const navigate = useNavigate();
  const [showSeatMap, setShowSeatMap] = useState(false);

  // Mock data as requested for a railway ticket details
  const ticketData = {
    ticketNumber: "PNR-8934-1102-45",
    status: "CONFIRMED",
    paymentStatus: "SUCCESS",
    source: "New Delhi (NDLS)",
    destiny: "Mumbai Central (MMCT)",
    journeyDate: "12 Oct 2026",
    journeyTime: "16:55 PM",
    duration: "15h 40m",
    bookedTime: "06 Oct 2026, 14:45 PM",
    trainName: "Rajdhani Express (12952)",
    seatInfo: "A1, Seat 22 Lower"
  };

  return (
    <div className="support-container">
      <div className="support-nav">
        <button className="back-btn" onClick={() => navigate('/login')}>
          <ArrowLeft size={20} /> Back to Login
        </button>
        <div className="nav-brand">
          <Train size={24} className="brand-icon" />
          <span>RailCare Support</span>
        </div>
        <button className="help-btn">
          <HeadphonesIcon size={20} /> Contact Support
        </button>
      </div>

      <div className="ticket-dashboard">
        <div className="ticket-header">
          <div className="header-info">
            <h2>Journey Details</h2>
            <p>Your complete itinerary and booking status</p>
          </div>
          <div className="ticket-badge">
            <Ticket size={24} />
            <span>e-Ticket</span>
          </div>
        </div>

        <div className="status-cards">
          <div className="status-card">
            <div className="card-icon"><CheckCircle2 size={24} /></div>
            <div className="card-content">
              <label>Ticket Status</label>
              <strong>{ticketData.status}</strong>
            </div>
          </div>
          <div className="status-card">
            <div className="card-icon payment"><CreditCard size={24} /></div>
            <div className="card-content">
              <label>Payment Status</label>
              <strong>{ticketData.paymentStatus}</strong>
            </div>
          </div>
          <div className="status-card">
            <div className="card-icon booked"><Clock size={24} /></div>
            <div className="card-content">
              <label>Booked On</label>
              <strong>{ticketData.bookedTime}</strong>
            </div>
          </div>
        </div>

        <div className="journey-card">
          <div className="train-info">
            <h3>{ticketData.trainName}</h3>
            <span>{ticketData.seatInfo}</span>
          </div>

          <div className="journey-timeline">
            <div className="timeline-point">
              <div className="point-icon"><MapPin size={20} /></div>
              <div className="point-details">
                <label>Source</label>
                <strong>{ticketData.source}</strong>
                <span>Departure: {ticketData.journeyTime}</span>
              </div>
            </div>

            <div className="timeline-connector">
              <Train size={20} className="connector-train" />
              <div className="line"></div>
              <span>{ticketData.duration}</span>
            </div>

            <div className="timeline-point">
              <div className="point-icon destination"><MapPin size={20} /></div>
              <div className="point-details">
                <label>Destiny</label>
                <strong>{ticketData.destiny}</strong>
                <span>Arrival: 11:45 AM</span>
              </div>
            </div>
          </div>

          <div className="journey-meta">
            <div className="meta-item">
              <Calendar size={18} />
              <span>Journey Date: <strong>{ticketData.journeyDate}</strong></span>
            </div>
            <div className="meta-item">
              <Ticket size={18} />
              <span>Ticket No: <strong>{ticketData.ticketNumber}</strong></span>
            </div>
          </div>
        </div>

        <div className="support-actions">
          <h3>Need help with this booking?</h3>
          <div className="action-buttons">
            <button className="action-btn secondary">Request Cancellation</button>
            <button className="action-btn secondary" onClick={() => setShowSeatMap(true)}>Change Seat</button>
            <button className="action-btn primary">Raise Support Ticket</button>
          </div>
        </div>
      </div>

      <AIAssistant />
      {showSeatMap && <SeatMap onClose={() => setShowSeatMap(false)} />}
    </div>
  );
};

export default SupportTicket;
