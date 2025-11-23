import { createContext, useState, useEffect, useContext } from 'react'
import {
  loginAccount,
  readSession,
} from '../services/api.jsx'

const AuthContext = createContext()

export const AuthProvider = ({ children }) => {
  const [user, setUser] = useState(null)
  const [session, setSession] = useState(null)

  useEffect(() => {
    const fetchUserProfile = async () => {
      try {
        const fetchSession = await readSession()
        if (fetchSession.status === 200) {
          setSession(fetchSession?.data?.session)
          setUser(fetchSession?.data?.session?.status)
        } else {
          setUser(null)
          setSession(null)
        }
      } catch (error) {
        setUser(null)
        setSession(null)
      }
    }
    fetchUserProfile()
  }, [])

  const login = async (data) => {
    try {
      let res = await loginAccount(data);
      return res;
    } catch (error) {
      return error
    }
  };

  return (
    <AuthContext.Provider value={{ user,session, login }}>
      {children}
    </AuthContext.Provider>
  )
}

export const useAuth = () => useContext(AuthContext)
