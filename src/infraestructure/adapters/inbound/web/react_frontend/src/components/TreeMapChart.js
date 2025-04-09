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
                    // Handle array values
                    if (Array.isArray(value) && value.length > 0) {
                        queryParams.append(key, value.join(','));
                    } 
                    // Handle numeric values like level_min and level_max - ensure they're included
                    else if ((typeof value === 'number' || typeof value === 'string') && value !== null && value !== undefined && String(value).trim() !== '') {
                        queryParams.append(key, value);
                    }
                });
            }

            console.log("TreeMapChart - Query params:", queryParams.toString());

            const response = await fetch(`http://localhost:8000/api/flights/origins-count?${queryParams}`);
            if (!response.ok) {
                throw new Error(`API error: ${response.status}`);
            }
            const responseData = await response.json();
            console.log("TreeMapChart - API response:", responseData);
            
            // Verify that responseData is an array
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
                console.error('Invalid data format received:', responseData);
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
            console.error('Error fetching origin count data:', error);
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

    // Make sure to re-fetch when filters change
    useEffect(() => {
        console.log("TreeMapChart - Filters changed:", filters);
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