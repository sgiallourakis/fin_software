import React from 'react';
import './App.css';
import UserForm from './components/UserForm';
import DataDisplay from './components/DataDisplay';


function App() {
	const [data, setData] = React.useState(null);

	const handleDataFetch = (fetchedData) => {
		setData(fetchedData);
	};

	return (
		<div className="App">
			<h1>Stock Assist</h1>
			<UserForm onDataFetch={handleDataFetch} />
			{data && <DataDisplay data={data} />}
		</div>
	);
}




