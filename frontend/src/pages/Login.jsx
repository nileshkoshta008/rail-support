import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Train, ShieldCheck, Mail, Lock, Phone, KeyRound, ArrowRight } from 'lucide-react';
import './Login.css';

const Login = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    username: '',
    password: '',
    mobile: '',
    otp: '',
    termsCode: '',
    agreeTerms: false
  });
  const [otpSent, setOtpSent] = useState(false);

  const handleInputChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: type === 'checkbox' ? checked : value
    }));
  };

  const handleSendOtp = () => {
    if (formData.mobile.length >= 10) {
      setOtpSent(true);
    } else {
      alert("Please enter a valid mobile number.");
    }
  };

  const handleLogin = (e) => {
    e.preventDefault();
    if (!formData.agreeTerms) {
      alert("Please agree to the Terms & Conditions.");
      return;
    }
    if (!otpSent || !formData.otp) {
      alert("Please generate and enter the OTP.");
      return;
    }
    // Simulate authentication
    navigate('/support');
  };

  return (
    <div className="login-container">
      <div className="login-wrapper">
        <div className="login-scenery">
          <div className="overlay">
            <Train size={64} className="train-icon" />
            <h2>Premium Rail Network</h2>
            <p>Your journey begins here. Log in to manage your bookings and access priority support.</p>
          </div>
        </div>
        
        <div className="login-form-container">
          <div className="form-header">
            <h3>Welcome Back</h3>
            <p>Enter your details to access your account</p>
          </div>

          <form onSubmit={handleLogin} className="login-form">
            <div className="input-group">
              <label>Username</label>
              <div className="input-with-icon">
                <Mail size={18} className="input-icon" />
                <input 
                  type="text" 
                  name="username" 
                  placeholder="Enter your email or username"
                  value={formData.username}
                  onChange={handleInputChange}
                  required 
                />
              </div>
            </div>

            <div className="input-group">
              <label>Password</label>
              <div className="input-with-icon">
                <Lock size={18} className="input-icon" />
                <input 
                  type="password" 
                  name="password" 
                  placeholder="Enter your password"
                  value={formData.password}
                  onChange={handleInputChange}
                  required 
                />
              </div>
            </div>

            <div className="input-group">
              <label>Mobile Number</label>
              <div className="input-with-icon mobile-input">
                <Phone size={18} className="input-icon" />
                <input 
                  type="tel" 
                  name="mobile" 
                  placeholder="10-digit mobile number"
                  value={formData.mobile}
                  onChange={handleInputChange}
                  required 
                />
                <button 
                  type="button" 
                  className={`otp-btn ${otpSent ? 'sent' : ''}`}
                  onClick={handleSendOtp}
                >
                  {otpSent ? 'Resend OTP' : 'Send OTP'}
                </button>
              </div>
            </div>

            {otpSent && (
              <div className="input-group otp-group fadeIn">
                <label>Enter OTP</label>
                <div className="input-with-icon">
                  <KeyRound size={18} className="input-icon" />
                  <input 
                    type="text" 
                    name="otp" 
                    placeholder="Enter 6-digit OTP"
                    value={formData.otp}
                    onChange={handleInputChange}
                    maxLength="6"
                    required 
                  />
                </div>
              </div>
            )}

            <div className="terms-section">
              <div className="input-group">
                <label>Terms Activation Code</label>
                <div className="input-with-icon">
                  <ShieldCheck size={18} className="input-icon" />
                  <input 
                    type="text" 
                    name="termsCode" 
                    placeholder="Enter Terms Code (Optional)"
                    value={formData.termsCode}
                    onChange={handleInputChange}
                  />
                </div>
              </div>

              <label className="checkbox-container">
                <input 
                  type="checkbox" 
                  name="agreeTerms" 
                  checked={formData.agreeTerms}
                  onChange={handleInputChange}
                />
                <span className="checkmark"></span>
                <span>I agree to the Terms & Conditions and Privacy Policy</span>
              </label>
            </div>

            <button type="submit" className="submit-btn gradient-btn">
              Proceed to Dashboard <ArrowRight size={18} />
            </button>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Login;
