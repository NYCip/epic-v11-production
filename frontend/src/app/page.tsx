'use client'

import { useSession } from 'next-auth/react'
import { useRouter } from 'next/navigation'
import { useEffect, useState } from 'react'
import { EmergencyOverride } from '@/components/EmergencyOverride'

interface BoardMember {
  name: string;
  role: string;
  status: 'active' | 'inactive';
  has_veto?: boolean;
}

export default function Dashboard() {
  const { data: session, status } = useSession()
  const router = useRouter()
  const [systemStatus, setSystemStatus] = useState<'normal' | 'halted' | 'degraded'>('normal')
  const [boardMembers, setBoardMembers] = useState<BoardMember[]>([])
  const [dashboardError, setDashboardError] = useState<string | null>(null)
  const [isLoadingSystemStatus, setIsLoadingSystemStatus] = useState(true)
  const [isLoadingBoardMembers, setIsLoadingBoardMembers] = useState(true)

  useEffect(() => {
    if (status === 'unauthenticated') {
      router.push('/login')
    }
  }, [status, router])

  useEffect(() => {
    if (session?.accessToken) {
      // Fetch system status
      fetchSystemStatus()
      // Fetch board members
      fetchBoardMembers()
    }
  }, [session])

  const fetchSystemStatus = async () => {
    setIsLoadingSystemStatus(true)
    setDashboardError(null)
    try {
      const response = await fetch('/api/control/system/override/status', {
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
        },
      })
      const data = await response.json()
      setSystemStatus(data.status.toLowerCase())
    } catch (error) {
      console.error('Failed to fetch system status:', error)
      setDashboardError('Failed to load system status. Please try again.')
    } finally {
      setIsLoadingSystemStatus(false)
    }
  }

  const fetchBoardMembers = async () => {
    setIsLoadingBoardMembers(true)
    setDashboardError(null)
    try {
      const response = await fetch('/api/agno/board/members')
      const data = await response.json()
      setBoardMembers(data.members || [])
    } catch (error) {
      console.error('Failed to fetch board members:', error)
      setDashboardError('Failed to load board members. Please try again.')
    } finally {
      setIsLoadingBoardMembers(false)
    }
  }

  const handleHalt = async (reason: string) => {
    try {
      const response = await fetch('/api/control/system/override/halt', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason }),
      })
      
      if (response.ok) {
        await fetchSystemStatus()
      } else {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to halt system')
      }
    } catch (error: any) {
      setDashboardError(error.message || 'An unexpected error occurred during halt operation.')
      console.error('Halt operation error:', error)
    }
  }

  const handleResume = async (reason: string) => {
    try {
      const response = await fetch('/api/control/system/override/resume', {
        method: 'POST',
        headers: {
          'Authorization': `Bearer ${session?.accessToken}`,
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ reason }),
      })
      
      if (response.ok) {
        await fetchSystemStatus()
      } else {
        const errorData = await response.json()
        throw new Error(errorData.detail || 'Failed to resume system')
      }
    } catch (error: any) {
      setDashboardError(error.message || 'An unexpected error occurred during resume operation.')
      console.error('Resume operation error:', error)
    }
  }

  if (status === 'loading') {
    return (
      <div
        className="flex items-center justify-center h-screen text-white text-xl"
        role="status"
        aria-live="polite"
      >
        <p>Loading application...</p>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gray-900 text-white p-8">
      <div className="max-w-7xl mx-auto">
        <h1 className="text-4xl font-bold mb-8">EPIC V11 Control Panel</h1>
        
        {dashboardError && (
          <div
            className="bg-red-900 text-red-200 p-4 rounded-lg mb-4"
            role="alert"
            aria-live="assertive"
          >
            {dashboardError}
          </div>
        )}

        {/* System Status */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8" aria-labelledby="system-status-heading">
          <h2 id="system-status-heading" className="text-2xl font-semibold mb-4">System Status</h2>
          {isLoadingSystemStatus ? (
            <p className="text-gray-400" aria-live="polite">Loading system status...</p>
          ) : (
            <div className="flex items-center gap-4">
              <div className={`w-4 h-4 rounded-full ${
                systemStatus === 'normal' ? 'bg-green-500' :
                systemStatus === 'halted' ? 'bg-red-500' : 'bg-yellow-500'
              }`} />
              <span className="text-lg capitalize">{systemStatus}</span>
            </div>
          )}
        </div>

        {/* Board Members */}
        <div className="bg-gray-800 rounded-lg p-6 mb-8" aria-labelledby="board-members-heading">
          <h2 id="board-members-heading" className="text-2xl font-semibold mb-4">AI Board of Directors</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {isLoadingBoardMembers ? (
              <p className="text-gray-400 col-span-full" aria-live="polite">Loading board members...</p>
            ) : boardMembers.length === 0 ? (
              <p className="text-gray-400 col-span-full" aria-live="polite">No board members found.</p>
            ) : (
              boardMembers.map((member) => (
              <div key={member.name} className="bg-gray-700 rounded-lg p-4">
                <h3 className="font-semibold">{member.name}</h3>
                <p className="text-sm text-gray-400">{member.role}</p>
                <div className="flex items-center gap-2 mt-2">
                  <div className={`w-2 h-2 rounded-full ${
                    member.status === 'active' ? 'bg-green-500' : 'bg-gray-500'
                  }`} />
                  <span className="text-xs">{member.status}</span>
                  {member.has_veto && (
                    <span className="text-xs bg-red-600 px-2 py-1 rounded">VETO</span>
                  )}
                </div>
              </div>
              ))
            )}
          </div>
        </div>

        {/* User Info */}
        <div className="bg-gray-800 rounded-lg p-6" aria-labelledby="user-info-heading">
          <h2 id="user-info-heading" className="text-2xl font-semibold mb-4">User Information</h2>
          <p>Email: {session?.user?.email}</p>
          <p>Role: <span className="capitalize">{session?.user?.role}</span></p>
        </div>
      </div>

      {/* Emergency Override - Only for Admins */}
      {session?.user?.role === 'admin' && (
        <EmergencyOverride
          onHalt={handleHalt}
          onResume={handleResume}
          systemStatus={systemStatus}
        />
      )}
    </div>
  )
}