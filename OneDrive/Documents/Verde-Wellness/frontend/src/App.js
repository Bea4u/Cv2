import React, { useState, useEffect } from 'react';
import { Calendar } from './components/ui/calendar';
import { Card, CardContent, CardDescription, CardFooter, CardHeader, CardTitle } from './components/ui/card';
import { Button } from './components/ui/button';
import { CalendarDays, Clock, User, MapPin, Leaf, Star } from 'lucide-react';
import './App.css';

function App() {
  const [selectedService, setSelectedService] = useState(null);
  const [selectedDate, setSelectedDate] = useState(null);
  const [selectedTime, setSelectedTime] = useState(null);
  const [showBooking, setShowBooking] = useState(false);
  const [services, setServices] = useState([]);
  const [availableSlots, setAvailableSlots] = useState([]);
  const [bookings, setBookings] = useState([]);

  const backendUrl = process.env.REACT_APP_BACKEND_URL;

  useEffect(() => {
    fetchServices();
  }, []);

  const fetchServices = async () => {
    try {
      const response = await fetch(`${backendUrl}/api/services`);
      if (response.ok) {
        const data = await response.json();
        setServices(data);
      }
    } catch (error) {
      console.error('Failed to fetch services:', error);
      // Fallback data for demo
      setServices([
        {
          id: '1',
          title: 'Premium Personal Training',
          description: 'One-on-one sessions with certified trainers, customized workout plans, progress tracking',
          price: 120,
          duration: '60 minutes',
          type: 'session'
        },
        {
          id: '2', 
          title: 'Holistic Nutrition Coaching',
          description: 'Personalized meal plans, grocery guides, weekly check-ins',
          price: 200,
          duration: 'Monthly',
          type: 'monthly'
        },
        {
          id: '3',
          title: 'Executive Wellness Package',
          description: 'Combined fitness, nutrition, and mindfulness coaching for busy leaders',
          price: 450,
          duration: 'Monthly',
          type: 'monthly'
        }
      ]);
    }
  };

  const fetchAvailableSlots = async (date) => {
    try {
      const response = await fetch(`${backendUrl}/api/availability?date=${date.toISOString()}`);
      if (response.ok) {
        const data = await response.json();
        setAvailableSlots(data);
      }
    } catch (error) {
      console.error('Failed to fetch availability:', error);
      // Fallback slots for demo
      setAvailableSlots([
        '09:00', '10:00', '11:00', '14:00', '15:00', '16:00', '17:00'
      ]);
    }
  };

  const handleServiceSelect = (service) => {
    setSelectedService(service);
    setShowBooking(true);
    setSelectedDate(null);
    setSelectedTime(null);
  };

  const handleDateSelect = (date) => {
    setSelectedDate(date);
    fetchAvailableSlots(date);
    setSelectedTime(null);
  };

  const handleBooking = async () => {
    if (!selectedService || !selectedDate || !selectedTime) return;

    try {
      const booking = {
        service_id: selectedService.id,
        service_title: selectedService.title,
        date: selectedDate.toISOString(),
        time: selectedTime,
        price: selectedService.price,
        status: 'confirmed'
      };

      const response = await fetch(`${backendUrl}/api/bookings`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(booking),
      });

      if (response.ok) {
        alert('Booking confirmed! We will contact you shortly.');
        setShowBooking(false);
        setSelectedService(null);
        setSelectedDate(null);
        setSelectedTime(null);
      }
    } catch (error) {
      console.error('Failed to create booking:', error);
      alert('Booking failed. Please try again.');
    }
  };

  const today = new Date();
  const futureDate = new Date();
  futureDate.setMonth(futureDate.getMonth() + 3);

  return (
    <div className="App">
      {/* Header */}
      <header className="header">
        <div className="container">
          <div className="nav">
            <div className="logo">
              <Leaf className="logo-icon" />
              <span className="logo-text">Verde Wellness</span>
            </div>
            <div className="contact-info">
              <span><MapPin size={16} /> Downtown Seattle</span>
              <span><Clock size={16} /> Mon-Fri 6AM-9PM</span>
            </div>
          </div>
        </div>
      </header>

      {/* Hero Section */}
      <section className="hero">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">Premium Wellness & Fitness</h1>
            <p className="hero-subtitle">
              Personalized training, nutrition coaching, and mindfulness programs 
              for busy professionals seeking work-life balance
            </p>
            <div className="hero-stats">
              <div className="stat">
                <Star className="stat-icon" />
                <span>4.9 Rating</span>
              </div>
              <div className="stat">
                <User className="stat-icon" />
                <span>500+ Clients</span>
              </div>
              <div className="stat">
                <Leaf className="stat-icon" />
                <span>Premium Experience</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {!showBooking ? (
        <>
          {/* Services Section */}
          <section className="services">
            <div className="container">
              <div className="section-header">
                <h2 className="section-title">Our Services</h2>
                <p className="section-subtitle">Choose your wellness journey</p>
              </div>
              
              <div className="services-grid">
                {services.map((service) => (
                  <Card key={service.id} className="service-card">
                    <CardHeader>
                      <CardTitle className="service-title">{service.title}</CardTitle>
                      <CardDescription className="service-description">
                        {service.description}
                      </CardDescription>
                    </CardHeader>
                    <CardContent>
                      <div className="service-details">
                        <div className="service-price">
                          ${service.price}<span className="price-unit">/{service.type}</span>
                        </div>
                        <div className="service-duration">
                          <Clock size={16} />
                          {service.duration}
                        </div>
                      </div>
                    </CardContent>
                    <CardFooter>
                      <Button 
                        onClick={() => handleServiceSelect(service)}
                        className="book-button"
                      >
                        Book Session
                      </Button>
                    </CardFooter>
                  </Card>
                ))}
              </div>
            </div>
          </section>

          {/* Promotion Section */}
          <section className="promotion">
            <div className="container">
              <div className="promotion-content">
                <h3 className="promotion-title">New Year, New You</h3>
                <p className="promotion-text">20% off first month for new members</p>
                <Button className="promotion-button">Learn More</Button>
              </div>
            </div>
          </section>
        </>
      ) : (
        /* Booking Section */
        <section className="booking">
          <div className="container">
            <div className="booking-content">
              <Button 
                onClick={() => setShowBooking(false)}
                className="back-button"
              >
                ← Back to Services
              </Button>
              
              <div className="booking-header">
                <h2 className="booking-title">Book Your Session</h2>
                <div className="selected-service">
                  <h3>{selectedService?.title}</h3>
                  <p>${selectedService?.price}/{selectedService?.type}</p>
                </div>
              </div>

              <div className="booking-form">
                <div className="booking-step">
                  <h4 className="step-title">
                    <CalendarDays size={20} />
                    Select Date
                  </h4>
                  <div className="calendar-container">
                    <Calendar
                      mode="single"
                      selected={selectedDate}
                      onSelect={handleDateSelect}
                      disabled={(date) => date < today || date > futureDate}
                      className="booking-calendar"
                    />
                  </div>
                </div>

                {selectedDate && (
                  <div className="booking-step">
                    <h4 className="step-title">
                      <Clock size={20} />
                      Select Time
                    </h4>
                    <div className="time-slots">
                      {availableSlots.map((slot) => (
                        <Button
                          key={slot}
                          onClick={() => setSelectedTime(slot)}
                          className={`time-slot ${selectedTime === slot ? 'selected' : ''}`}
                        >
                          {slot}
                        </Button>
                      ))}
                    </div>
                  </div>
                )}

                {selectedDate && selectedTime && (
                  <div className="booking-summary">
                    <h4 className="step-title">Booking Summary</h4>
                    <div className="summary-details">
                      <p><strong>Service:</strong> {selectedService.title}</p>
                      <p><strong>Date:</strong> {selectedDate.toLocaleDateString()}</p>
                      <p><strong>Time:</strong> {selectedTime}</p>
                      <p><strong>Price:</strong> ${selectedService.price}</p>
                    </div>
                    <Button 
                      onClick={handleBooking}
                      className="confirm-button"
                    >
                      Confirm Booking
                    </Button>
                  </div>
                )}
              </div>
            </div>
          </div>
        </section>
      )}

      {/* Footer */}
      <footer className="footer">
        <div className="container">
          <div className="footer-content">
            <div className="footer-section">
              <div className="logo">
                <Leaf className="logo-icon" />
                <span className="logo-text">Verde Wellness</span>
              </div>
              <p>Premium wellness and fitness for busy professionals</p>
            </div>
            <div className="footer-section">
              <h4>Contact</h4>
              <p>📧 hello@verdewellness.com</p>
              <p>📞 (206) 555-VERDE</p>
              <p>📍 Downtown Seattle</p>
            </div>
            <div className="footer-section">
              <h4>Hours</h4>
              <p>Monday-Friday: 6AM-9PM</p>
              <p>Saturday-Sunday: 8AM-6PM</p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  );
}

export default App;