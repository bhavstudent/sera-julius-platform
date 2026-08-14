/**
 * useAuth — thin re-export from AuthContext so new TSX panels can import
 * from '../auth/useAuth' without touching the legacy JSX context file.
 */
// eslint-disable-next-line @typescript-eslint/ban-ts-comment
// @ts-ignore – AuthContext is a JS file, types inferred at runtime
export { useAuth } from '../context/AuthContext'
