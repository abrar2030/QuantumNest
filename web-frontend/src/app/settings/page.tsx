'use client';

import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { Card } from '@/components/ui/Card';
import { Button } from '@/components/ui/Button';
import { getSettings, updateSettings, validateSettings } from '@/lib/settings';

interface SettingsState {
  theme: string;
  language: string;
  notifications: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  security: {
    twoFactor: boolean;
    biometrics: boolean;
  };
  privacy: {
    dataSharing: boolean;
    analytics: boolean;
  };
  loading: boolean;
  error: string | null;
  success: string | null;
}

export default function Settings() {
  const router = useRouter();
  const [settings, setSettings] = useState<SettingsState>({
    theme: 'dark',
    language: 'en',
    notifications: {
      email: true,
      push: true,
      sms: false,
    },
    security: {
      twoFactor: false,
      biometrics: false,
    },
    privacy: {
      dataSharing: true,
      analytics: true,
    },
    loading: true,
    error: null,
    success: null,
  });

  const [showPasswordModal, setShowPasswordModal] = useState(false);
  const [passwordData, setPasswordData] = useState({
    currentPassword: '',
    newPassword: '',
    confirmPassword: '',
  });

  useEffect(() => {
    const fetchSettings = async () => {
      try {
        const userSettings = await getSettings();
        setSettings(prevSettings => ({
          ...prevSettings,
          ...userSettings,
          loading: false,
        }));
      } catch (error) {
        console.error('Error fetching settings:', error);
        setSettings(prevSettings => ({
          ...prevSettings,
          loading: false,
          error: 'Error loading settings. Please try again later.',
        }));
      }
    };

    fetchSettings();
  }, []);

  const handleThemeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      theme: e.target.value,
    }));
  };

  const handleLanguageChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSettings(prevSettings => ({
      ...prevSettings,
      language: e.target.value,
    }));
  };

  const handleNotificationToggle = (type: 'email' | 'push' | 'sms') => {
    setSettings(prevSettings => ({
      ...prevSettings,
      notifications: {
        ...prevSettings.notifications,
        [type]: !prevSettings.notifications[type],
      },
    }));
  };

  const handleSecurityToggle = (type: 'twoFactor' | 'biometrics') => {
    setSettings(prevSettings => ({
      ...prevSettings,
      security: {
        ...prevSettings.security,
        [type]: !prevSettings.security[type],
      },
    }));
  };

  const handlePrivacyToggle = (type: 'dataSharing' | 'analytics') => {
    setSettings(prevSettings => ({
      ...prevSettings,
      privacy: {
        ...prevSettings.privacy,
        [type]: !prevSettings.privacy[type],
      },
    }));
  };

  const handlePasswordChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    setPasswordData({
      ...passwordData,
      [e.target.name]: e.target.value,
    });
  };

  const handlePasswordSubmit = async () => {
    if (passwordData.newPassword !== passwordData.confirmPassword) {
      setSettings(prevSettings => ({
        ...prevSettings,
        error: 'New passwords do not match',
        success: null,
      }));
      return;
    }

    try {
      await updateSettings({ password: passwordData.newPassword });
      setShowPasswordModal(false);
      setPasswordData({
        currentPassword: '',
        newPassword: '',
        confirmPassword: '',
      });
      setSettings(prevSettings => ({
        ...prevSettings,
        success: 'Password updated successfully',
        error: null,
      }));
    } catch (error) {
      console.error('Error updating password:', error);
      setSettings(prevSettings => ({
        ...prevSettings,
        error: 'Error updating password. Please try again.',
        success: null,
      }));
    }
  };

  const handleSave = async () => {
    setSettings(prevSettings => ({
      ...prevSettings,
      loading: true,
      error: null,
      success: null,
    }));

    try {
      const isValid = await validateSettings(settings);
      if (!isValid) {
        setSettings(prevSettings => ({
          ...prevSettings,
          loading: false,
          error: 'Invalid settings. Please check your inputs.',
        }));
        return;
      }

      await updateSettings(settings);
      setSettings(prevSettings => ({
        ...prevSettings,
        loading: false,
        success: 'Settings saved successfully',
      }));
    } catch (error) {
      console.error('Error saving settings:', error);
      setSettings(prevSettings => ({
        ...prevSettings,
        loading: false,
        error: 'Error saving settings. Please try again later.',
      }));
    }
  };

  const handleCancel = () => {
    router.push('/dashboard');
  };

  if (settings.loading) {
    return (
      <div className="container mx-auto p-6">
        <h1 className="text-3xl font-bold mb-6">Settings</h1>
        <div className="flex justify-center items-center h-64">
          <p className="text-lg">Loading settings...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="container mx-auto p-6">
      <h1 className="text-3xl font-bold mb-6">Settings</h1>

      {settings.error && (
        <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
          {settings.error}
        </div>
      )}

      {settings.success && (
        <div className="bg-green-100 border border-green-400 text-green-700 px-4 py-3 rounded mb-4">
          {settings.success}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Appearance</h2>
          
          <div className="mb-4">
            <label className="block text-sm font-medium mb-2" htmlFor="theme">
              Theme
            </label>
            <select
              id="theme"
              className="w-full p-2 border rounded"
              value={settings.theme}
              onChange={handleThemeChange}
              aria-label="theme"
            >
              <option value="light">Light</option>
              <option value="dark">Dark</option>
              <option value="system">System</option>
            </select>
          </div>

          <div className="mb-4">
            <label className="block text-sm font-medium mb-2" htmlFor="language">
              Language
            </label>
            <select
              id="language"
              className="w-full p-2 border rounded"
              value={settings.language}
              onChange={handleLanguageChange}
              aria-label="language"
            >
              <option value="en">English</option>
              <option value="es">Spanish</option>
              <option value="fr">French</option>
              <option value="de">German</option>
              <option value="zh">Chinese</option>
              <option value="ja">Japanese</option>
            </select>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Notifications</h2>
          
          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="mr-2"
                checked={settings.notifications.email}
                onChange={() => handleNotificationToggle('email')}
                aria-label="email"
              />
              <span>Email Notifications</span>
            </label>
          </div>

          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="mr-2"
                checked={settings.notifications.push}
                onChange={() => handleNotificationToggle('push')}
                aria-label="push"
              />
              <span>Push Notifications</span>
            </label>
          </div>

          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="mr-2"
                checked={settings.notifications.sms}
                onChange={() => handleNotificationToggle('sms')}
                aria-label="sms"
              />
              <span>SMS Notifications</span>
            </label>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Security</h2>
          
          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="mr-2"
                checked={settings.security.twoFactor}
                onChange={() => handleSecurityToggle('twoFactor')}
                aria-label="two-factor"
              />
              <span>Two-Factor Authentication</span>
            </label>
          </div>

          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="mr-2"
                checked={settings.security.biometrics}
                onChange={() => handleSecurityToggle('biometrics')}
                aria-label="biometrics"
              />
              <span>Biometric Authentication</span>
            </label>
          </div>

          <div className="mt-6">
            <Button 
              onClick={() => setShowPasswordModal(true)}
              aria-label="change password"
            >
              Change Password
            </Button>
          </div>
        </Card>

        <Card className="p-6">
          <h2 className="text-xl font-semibold mb-4">Privacy</h2>
          
          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="mr-2"
                checked={settings.privacy.dataSharing}
                onChange={() => handlePrivacyToggle('dataSharing')}
                aria-label="data-sharing"
              />
              <span>Data Sharing</span>
            </label>
            <p className="text-sm text-gray-500 mt-1">
              Allow sharing anonymized data to improve our services
            </p>
          </div>

          <div className="mb-4">
            <label className="flex items-center">
              <input
                type="checkbox"
                className="mr-2"
                checked={settings.privacy.analytics}
                onChange={() => handlePrivacyToggle('analytics')}
                aria-label="analytics"
              />
              <span>Usage Analytics</span>
            </label>
            <p className="text-sm text-gray-500 mt-1">
              Allow collection of usage data to improve your experience
            </p>
          </div>
        </Card>
      </div>

      <div className="mt-8 flex justify-end space-x-4">
        <Button 
          variant="secondary" 
          onClick={handleCancel}
          aria-label="cancel"
        >
          Cancel
        </Button>
        <Button 
          onClick={handleSave}
          aria-label="save"
        >
          Save Settings
        </Button>
      </div>

      {showPasswordModal && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white p-6 rounded-lg w-full max-w-md">
            <h2 className="text-xl font-semibold mb-4">Change Password</h2>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2" htmlFor="currentPassword">
                Current Password
              </label>
              <input
                type="password"
                id="currentPassword"
                name="currentPassword"
                className="w-full p-2 border rounded"
                value={passwordData.currentPassword}
                onChange={handlePasswordChange}
              />
            </div>
            
            <div className="mb-4">
              <label className="block text-sm font-medium mb-2" htmlFor="newPassword">
                New Password
              </label>
              <input
                type="password"
                id="newPassword"
                name="newPassword"
                className="w-full p-2 border rounded"
                value={passwordData.newPassword}
                onChange={handlePasswordChange}
              />
            </div>
            
            <div className="mb-6">
              <label className="block text-sm font-medium mb-2" htmlFor="confirmPassword">
                Confirm New Password
              </label>
              <input
                type="password"
                id="confirmPassword"
                name="confirmPassword"
                className="w-full p-2 border rounded"
                value={passwordData.confirmPassword}
                onChange={handlePasswordChange}
              />
            </div>
            
            <div className="flex justify-end space-x-4">
              <Button 
                variant="secondary" 
                onClick={() => setShowPasswordModal(false)}
              >
                Cancel
              </Button>
              <Button onClick={handlePasswordSubmit}>
                Update Password
              </Button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
