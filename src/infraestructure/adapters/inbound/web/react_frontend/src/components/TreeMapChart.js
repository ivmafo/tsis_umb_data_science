import React, { useState, useEffect } from 'react';
import { Treemap, ResponsiveContainer, Tooltip } from 'recharts';
import './TreeMapChart.css';

function TreeMapChart({ filters }) {
    const [data, setData] = useState([]);
    const [isLoading, setIsLoading] = useState(false);

    const fetchData = async () => {
        setIsLoading(true);
        try {
            // Create query parameters from filters
            const queryParams = new URLSearchParams();
            if (filters) {
                Object.entries(filters).forEach(([key, value]) => {
                    if (Array.isArray(value) && value.length > 0) {
                        queryParams.append(key, value.join(','));
                    }
                });
            }

            const response = await fetch(`http://localhost:8000/api/flights/origins-count?${queryParams}`);
            const responseData = await response.json();
            
            // Verificar que responseData sea un array
            if (Array.isArray(responseData) && responseData.length > 0) {
                // Transform data for TreeMap
                const transformedData = {
                    name: 'Origins',
                    children: responseData.map(item => ({
                        name: item.origin || 'Unknown',
                        size: item.count || 0,
                        fill: `hsl(${Math.random() * 360}, 70%, 50%)`
                    }))
                };
                setData([transformedData]);
            } else {
                setData([{
                    name: 'Origins',
                    children: [{
                        name: 'No data',
                        size: 1,
                        fill: '#cccccc'
                    }]
                }]);
            }
        } catch (error) {
            console.error('Error fetching origin counts:', error);
            setData([{
                name: 'Origins',
                children: [{
                    name: 'Error',
                    size: 1,
                    fill: '#ff0000'
                }]
            }]);
        } finally {
            setIsLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
    }, [filters]);

    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length > 0) {
            const data = payload[0].payload;
            return (
                <div className="treemap-tooltip">
                    <p>{`Origin: ${data.name}`}</p>
                    <p>{`Count: ${data.size}`}</p>
                </div>
            );
        }
        return null;
    };

    return (
        <div className="treemap-card">
            <div className="treemap-header">
                <h3>Distribucion de Vuelos por Origen</h3>
                <button 
                    onClick={fetchData}
                    disabled={isLoading}
                    className="refresh-button"
                >
                    {isLoading ? 'Loading...' : 'Refrescar Origenes'}
                </button>
            </div>
            <div className="treemap-container">
                {data.length > 0 ? (
                    <ResponsiveContainer width="100%" height={300}>
                        <Treemap
                            data={data}
                            dataKey="size"
                            aspectRatio={4/3}
                            stroke="#fff"
                            fill="#8884d8"
                        >
                            <Tooltip content={<CustomTooltip />} />
                        </Treemap>
                    </ResponsiveContainer>
                ) : (
                    <div className="no-data">No data available</div>
                )}
            </div>
        </div>
    );
}

export default TreeMapChart;