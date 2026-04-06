import React, { useState } from 'react';
import { TrainFront, X, Check, ArrowLeft } from 'lucide-react';
import './SeatMap.css';

const COACHES = ['ENG', 'GEN', 'S1', 'S2', 'B1', 'B2', 'A1', 'A2'];

const SEAT_TYPES = {
  LB: 'Lower Berth',
  MB: 'Middle Berth',
  UB: 'Upper Berth',
  SL: 'Side Lower',
  SU: 'Side Upper'
};

const SeatMap = ({ onClose }) => {
  const [selectedCoach, setSelectedCoach] = useState('B1');
  const [selectedSeat, setSelectedSeat] = useState(null);

  // Generate dummy seats for a coach
  const generateSeats = () => {
    const layout = [];
    let seatNo = 1;
    for (let compartment = 0; compartment < 4; compartment++) {
      const db = [
        { id: seatNo++, type: 'LB' },
        { id: seatNo++, type: 'MB' },
        { id: seatNo++, type: 'UB' },
        { id: seatNo++, type: 'LB' },
        { id: seatNo++, type: 'MB' },
        { id: seatNo++, type: 'UB' },
      ];
      const side = [
        { id: seatNo++, type: 'SL' },
        { id: seatNo++, type: 'SU' }
      ];
      layout.push({ compartment, main: db, side });
    }
    return layout;
  };

  const handleSeatClick = (seat) => {
    setSelectedSeat(seat);
  };

  return (
    <div className="seat-map-overlay">
      <div className="seat-map-modal">
        <div className="smt-header">
          <div className="smt-title">
            <button className="icon-btn" onClick={onClose}><ArrowLeft size={24} /></button>
            <h2>Seat Selection</h2>
          </div>
          <button className="icon-btn close" onClick={onClose}><X size={24} /></button>
        </div>

        <div className="train-overview-section">
          <h3>Train Composition</h3>
          <p>Select a coach from Engine to last Dibba</p>
          <div className="train-composition">
            <div className="train-track"></div>
            {COACHES.map(coach => (
              <div 
                key={coach} 
                className={`coach-box ${coach === 'ENG' ? 'engine' : ''} ${selectedCoach === coach ? 'selected' : ''}`}
                onClick={() => coach !== 'ENG' && setSelectedCoach(coach)}
              >
                {coach === 'ENG' ? <TrainFront size={24} /> : <span>{coach}</span>}
              </div>
            ))}
          </div>
        </div>

        <div className="coach-layout-section">
          <div className="coach-header">
            <h3>Coach {selectedCoach}</h3>
            <div className="seat-legend">
              <span className="legend-item"><span className="box available"></span> Available</span>
              <span className="legend-item"><span className="box booked"></span> Booked</span>
              <span className="legend-item"><span className="box selected"></span> Selected</span>
            </div>
          </div>

          <div className="coach-interior-wrapper">
            <div className="coach-interior">
              {generateSeats().map((comp) => (
                <div key={comp.compartment} className="compartment">
                  <div className="main-berths">
                    {comp.main.map(seat => (
                      <div 
                        key={seat.id}
                        className={`seat-item ${selectedSeat?.id === seat.id ? 'selected' : 'available'}`}
                        onClick={() => handleSeatClick(seat)}
                        title={`${seat.id} - ${SEAT_TYPES[seat.type]}`}
                      >
                        <span className="seat-num">{seat.id}</span>
                        <span className="seat-type">{seat.type}</span>
                      </div>
                    ))}
                  </div>
                  <div className="aisle">Aisle</div>
                  <div className="side-berths">
                    {comp.side.map(seat => (
                       <div 
                       key={seat.id}
                       className={`seat-item side ${selectedSeat?.id === seat.id ? 'selected' : 'available'}`}
                       onClick={() => handleSeatClick(seat)}
                       title={`${seat.id} - ${SEAT_TYPES[seat.type]}`}
                     >
                       <span className="seat-num">{seat.id}</span>
                       <span className="seat-type">{seat.type}</span>
                     </div>
                    ))}
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>

        {selectedSeat && (
          <div className="booking-footer slideUp">
            <div className="selection-details">
              <h4>Seat Selected</h4>
              <p>Coach {selectedCoach} | Seat {selectedSeat.id} ({SEAT_TYPES[selectedSeat.type]})</p>
            </div>
            <button className="confirm-btn" onClick={() => {
              alert(`Seat ${selectedCoach}-${selectedSeat.id} successfully requested!`);
              onClose();
            }}>
              Confirm Booking <Check size={18} />
            </button>
          </div>
        )}
      </div>
    </div>
  );
};

export default SeatMap;
