import React, { useState, useEffect } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';
import './TreeMapChart.css';

function FlightTypeBarChart({ filters }) {
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            const queryParams = new URLSearchParams();
            if (filters) {
                Object.entries(filters).forEach(([key, value]) => {
                    if (Array.isArray(value) && value.length > 0) {
                        queryParams.append(key, value.join(','));
                    }
                });
            }

            const response = await fetch(`http://localhost:8000/api/flights/flight-types-count?${queryParams}`);
            const responseData = await response.json();
            
            if (Array.isArray(responseData) && responseData.length > 0) {
                setData(responseData.map(item => ({
                    name: item.flight_type || 'Unknown',
                    value: item.count || 0
                })));
            } else {
                setData([]);
            }
        } catch (error) {
            console.error('Error fetching flight type counts:', error);
            setData([]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [filters]);

    return (
        <div className="chart-card">
            <div className="chart-header">
                <h3>Flight Types Distribution</h3>
                <button 
                    onClick={fetchData}
                    disabled={isLoading}
                    className="refresh-button"
                >
                    {isLoading ? 'Loading...' : 'Refresh Chart'}
                </button>
            </div>
            <div className="chart-container">
                {data.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                        <BarChart data={data} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                            <CartesianGrid strokeDasharray="3 3" />
                            <XAxis dataKey="name" angle={-45} textAnchor="end" height={100} />
                            <YAxis />
                            <Tooltip />
                            <Bar dataKey="value" fill="#8884d8" name="Count" />
                        </BarChart>
                    </ResponsiveContainer>
                ) : (
                    <div className="no-data">No data available</div>
                )}
            </div>
        </div>
    );
}

export default FlightTypeBarChart;