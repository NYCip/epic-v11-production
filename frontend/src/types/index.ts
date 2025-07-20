export interface User {
  id: string
  email: string
  full_name: string
  role: 'admin' | 'operator' | 'viewer'
  is_active: boolean
  created_at: string
  last_login?: string
}

export interface SystemStatus {
  status: 'normal' | 'halted' | 'degraded'
  override?: {
    type: string
    id: string
    initiated_by: string
    timestamp: string
  }
}

export interface BoardMember {
  name: string
  role: string
  model: string
  has_veto: boolean
  status: 'active' | 'inactive'
}

export interface BoardDecision {
  query: string
  decision: 'APPROVED' | 'REJECTED' | 'DEFERRED'
  risk_level: 'LOW' | 'MEDIUM' | 'HIGH' | 'CRITICAL' | 'EXTREME'
  consensus_reason: string
  timestamp: string
}

export interface AuditLog {
  id: string
  user_id?: string
  action: string
  resource?: string
  resource_id?: string
  success: boolean
  error_message?: string
  timestamp: string
}