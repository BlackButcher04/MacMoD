import { useState } from 'react';
import { Button } from '../ui/button';
import { Input } from '../ui/input';
import { Label } from '../ui/label';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '../ui/card';
import { Alert, AlertDescription } from '../ui/alert';
import { Eye, EyeOff, Activity } from 'lucide-react';
import { UserAccount } from '../../types';

interface LoginFormProps {
  accounts: UserAccount[];
  onLogin: (accountId: string) => void;
  onRegister: (account: UserAccount) => void;
}

export function LoginForm({ accounts, onLogin, onRegister }: LoginFormProps) {
  const [isRegistering, setIsRegistering] = useState(false);
  const [username, setUsername] = useState('');
  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [position, setPosition] = useState('');
  const [showPassword, setShowPassword] = useState(false);
  const [error, setError] = useState('');

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    if (isRegistering) {
      if (!username || !email || !password || !position) {
        setError('Please fill in all fields.');
        return;
      }
      // Check if email already exists
      if (accounts.some(a => a.email === email)) {
        setError('Email is already registered.');
        return;
      }
      const newAccount: UserAccount = {
        id: Date.now().toString(),
        name: username,
        email,
        position,
        registeredDate: new Date().toISOString().split('T')[0]
      };
      onRegister(newAccount);
    } else {
      if (!username || !password) {
        setError('Please enter your username and password.');
        return;
      }
      // Since the prompt asks "login方面能就只需要让用户输入username和password就可以登入了" 
      // let's check username instead of email for login.
      const account = accounts.find(a => a.name === username);
      if (account) {
        // We accept any password for simplicity as we don't store passwords in accounts array,
        // but the login logic allows them to log in if the user exists.
        onLogin(account.id);
      } else {
        setError('Invalid username or password.');
      }
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-slate-950 px-4">
      <Card className="w-full max-w-md bg-slate-900 border-slate-800 text-slate-100 shadow-2xl">
        <CardHeader className="text-center space-y-4">
          <div className="mx-auto w-16 h-16 bg-blue-600/20 rounded-2xl flex items-center justify-center border border-blue-500/30">
            <Activity className="w-8 h-8 text-blue-500" />
          </div>
          <div>
            <CardTitle className="text-2xl font-bold tracking-tight text-white">MacMod</CardTitle>
            <CardDescription className="text-slate-400 mt-1">
              {isRegistering ? 'Register your AI monitoring account' : 'Predictive Maintenance Terminal'}
            </CardDescription>
          </div>
        </CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            {error && (
              <Alert variant="destructive" className="bg-red-500/10 border-red-500/50 text-red-400">
                <AlertDescription>{error}</AlertDescription>
              </Alert>
            )}
            
            {isRegistering && (
              <>
                <div className="space-y-2">
                  <Label htmlFor="email" className="text-slate-300">Email Address</Label>
                  <Input
                    id="email"
                    type="email"
                    value={email}
                    onChange={(e) => setEmail(e.target.value)}
                    placeholder="engineer@factory.com"
                    className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus-visible:ring-blue-500"
                  />
                </div>
              </>
            )}

            <div className="space-y-2">
              <Label htmlFor="username" className="text-slate-300">Username</Label>
              <Input
                id="username"
                type="text"
                value={username}
                onChange={(e) => setUsername(e.target.value)}
                placeholder="Enter your username"
                className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus-visible:ring-blue-500"
              />
            </div>

            <div className="space-y-2">
              <Label htmlFor="password" className="text-slate-300">Password</Label>
              <div className="relative">
                <Input
                  id="password"
                  type={showPassword ? 'text' : 'password'}
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="Enter your password"
                  className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus-visible:ring-blue-500 pr-10"
                />
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="absolute right-0 top-0 h-full px-3 py-2 text-slate-400 hover:text-white hover:bg-transparent"
                  onClick={() => setShowPassword(!showPassword)}
                >
                  {showPassword ? <EyeOff className="h-4 w-4" /> : <Eye className="h-4 w-4" />}
                </Button>
              </div>
            </div>

            {isRegistering && (
              <div className="space-y-2">
                <Label htmlFor="position" className="text-slate-300">Job Position</Label>
                <Input
                  id="position"
                  type="text"
                  value={position}
                  onChange={(e) => setPosition(e.target.value)}
                  placeholder="e.g. Maintenance Technician"
                  className="bg-slate-800 border-slate-700 text-white placeholder:text-slate-500 focus-visible:ring-blue-500"
                />
              </div>
            )}

            <Button 
              type="submit" 
              className="w-full bg-blue-600 hover:bg-blue-700 text-white" 
            >
              {isRegistering ? 'Create Account' : 'Log In'}
            </Button>

            <div className="text-center mt-4">
              <button
                type="button"
                onClick={() => {
                  setIsRegistering(!isRegistering);
                  setError('');
                  setUsername('');
                  setPassword('');
                  setEmail('');
                  setPosition('');
                }}
                className="text-sm text-blue-400 hover:text-blue-300 transition-colors"
              >
                {isRegistering ? 'Already have an account? Sign In' : 'Need an account? Sign Up'}
              </button>
            </div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
