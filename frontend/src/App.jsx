import { useState } from 'react';
import Register from './components/Register';
import Login from './components/Login';
import PasswordManager from './components/PasswordManager';

function App() {
  const [loggedIn, setLoggedIn] = useState(false);

  return (
    <div className="App">
      {!loggedIn ? (
        <>
          <Register />
          <Login setLoggedIn={setLoggedIn} />
        </>
      ) : (
        <PasswordManager />
      )}
    </div>
  );
}

export default App;
