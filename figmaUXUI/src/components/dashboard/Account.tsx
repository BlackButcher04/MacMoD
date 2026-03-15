import { Card, CardContent, CardHeader, CardTitle, CardDescription } from '../ui/card';
import { Button } from '../ui/button';
import { Badge } from '../ui/badge';
import { User, Mail, Briefcase, Calendar, Shield, Plus } from 'lucide-react';
import { UserAccount, LogEntry } from '../../types';

interface AccountProps {
  account: UserAccount;
  onAddAccountClick: () => void;
  userLogs: LogEntry[];
}

export function Account({ account, onAddAccountClick, userLogs }: AccountProps) {
  const registrationDate = account.registeredDate || '2024-01-15';
  const accountAge = Math.floor((new Date().getTime() - new Date(registrationDate).getTime()) / (1000 * 60 * 60 * 24));

  const formatTimeAgo = (timestamp: string) => {
    const diff = Date.now() - new Date(timestamp).getTime();
    const minutes = Math.floor(diff / 60000);
    const hours = Math.floor(minutes / 60);
    const days = Math.floor(hours / 24);
    if (days > 0) return `${days} day${days > 1 ? 's' : ''} ago`;
    if (hours > 0) return `${hours} hour${hours > 1 ? 's' : ''} ago`;
    if (minutes > 0) return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
    return 'Just now';
  };

  return (
    <div className="p-6 max-w-5xl mx-auto space-y-6">
      <div>
        <h1 className="text-2xl font-semibold text-gray-900">Account Information</h1>
        <p className="text-gray-600 mt-1">View and manage your profile details.</p>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Profile Card */}
        <Card className="lg:col-span-2">
          <CardHeader>
            <CardTitle className="flex items-center gap-2">
              <User className="w-5 h-5 text-blue-500" />
              Profile Details
            </CardTitle>
            <CardDescription>Your MacMod account information</CardDescription>
          </CardHeader>
          <CardContent className="space-y-6">
            <div className="flex items-start gap-6">
              <div className="w-24 h-24 bg-blue-600 rounded-full flex items-center justify-center shrink-0">
                <span className="text-3xl font-bold text-white">
                  {account.name.split(' ').map(n => n[0]).join('').toUpperCase().substring(0, 2)}
                </span>
              </div>
              <div className="flex-1">
                <h2 className="text-2xl font-semibold text-gray-900">{account.name}</h2>
                <p className="text-gray-600 mt-1">{account.position}</p>
                <Badge variant="outline" className="mt-3 bg-blue-50 text-blue-700 border-blue-200">
                  Active Account
                </Badge>
              </div>
            </div>

            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 pt-4 border-t">
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-gray-500 text-sm">
                  <Mail className="w-4 h-4" />
                  <span>Email Address</span>
                </div>
                <p className="text-gray-900 font-medium pl-6">{account.email}</p>
              </div>

              <div className="space-y-1">
                <div className="flex items-center gap-2 text-gray-500 text-sm">
                  <Briefcase className="w-4 h-4" />
                  <span>Job Position</span>
                </div>
                <p className="text-gray-900 font-medium pl-6">{account.position}</p>
              </div>

              <div className="space-y-1">
                <div className="flex items-center gap-2 text-gray-500 text-sm">
                  <Calendar className="w-4 h-4" />
                  <span>Registration Date</span>
                </div>
                <p className="text-gray-900 font-medium pl-6">{registrationDate}</p>
              </div>

              <div className="space-y-1">
                <div className="flex items-center gap-2 text-gray-500 text-sm">
                  <Shield className="w-4 h-4" />
                  <span>Account ID</span>
                </div>
                <p className="text-gray-900 font-medium pl-6">{account.id}</p>
              </div>
            </div>
          </CardContent>
        </Card>

        {/* Quick Stats */}
        <div className="space-y-6">
          {/* Add New Account Card */}
          <Card className="border-dashed border-2 hover:border-blue-500 hover:bg-blue-50/50 cursor-pointer transition-colors group" onClick={onAddAccountClick}>
            <CardContent className="p-6 flex flex-col items-center justify-center text-center space-y-3">
              <div className="w-12 h-12 rounded-full bg-blue-100 group-hover:bg-blue-200 flex items-center justify-center transition-colors">
                <Plus className="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 className="font-medium text-gray-900">Add New Account</h3>
                <p className="text-sm text-gray-500 mt-1">Create an additional user profile</p>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Account Status</CardTitle>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Status</span>
                <Badge className="bg-green-100 text-green-800 border-green-200">Active</Badge>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Role</span>
                <span className="text-sm font-medium text-gray-900">{account.position}</span>
              </div>
              <div className="flex items-center justify-between">
                <span className="text-sm text-gray-600">Access Level</span>
                <Badge variant="outline" className="bg-blue-50 text-blue-700 border-blue-200">Full</Badge>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <CardTitle className="text-base">Security</CardTitle>
            </CardHeader>
            <CardContent className="space-y-3">
              <Button variant="outline" className="w-full justify-start" size="sm">
                Change Password
              </Button>
              <Button variant="outline" className="w-full justify-start" size="sm">
                Two-Factor Auth
              </Button>
              <Button variant="outline" className="w-full justify-start" size="sm">
                Session History
              </Button>
            </CardContent>
          </Card>
        </div>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>Recent Activity</CardTitle>
          <CardDescription>Your latest actions in the MacMod system</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-3">
            {userLogs.length > 0 ? userLogs.slice(0, 5).map(log => (
              <div key={log.id} className="flex items-start gap-3 p-3 border rounded-lg">
                <div className={`w-2 h-2 rounded-full mt-2 ${
                  log.type === 'alert_critical' ? 'bg-red-500' :
                  log.type === 'maintenance_scheduled' ? 'bg-orange-500' :
                  log.type === 'model_updated' ? 'bg-green-500' :
                  'bg-blue-500'
                }`}></div>
                <div className="flex-1">
                  <p className="text-sm font-medium">{log.action}</p>
                  <p className="text-xs text-gray-500 mt-1">{formatTimeAgo(log.timestamp)}</p>
                </div>
              </div>
            )) : (
              <div className="text-center p-4 text-gray-500 text-sm">No recent activity found for your account.</div>
            )}
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
