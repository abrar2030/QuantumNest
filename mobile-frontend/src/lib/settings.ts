// lib/settings.ts - Settings management utilities

interface Settings {
  theme?: string;
  language?: string;
  notifications?: {
    email: boolean;
    push: boolean;
    sms: boolean;
  };
  security?: {
    twoFactor: boolean;
    biometrics: boolean;
  };
  privacy?: {
    dataSharing: boolean;
    analytics: boolean;
  };
  password?: string;
}

/**
 * Get user settings from local storage or API
 */
export async function getSettings(): Promise<Settings> {
  try {
    // Try to get from localStorage first
    if (typeof window !== "undefined") {
      const savedSettings = localStorage.getItem("userSettings");
      if (savedSettings) {
        return JSON.parse(savedSettings);
      }
    }

    // Return default settings
    return {
      theme: "dark",
      language: "en",
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
    };
  } catch (error) {
    console.error("Error getting settings:", error);
    throw error;
  }
}

/**
 * Update user settings
 */
export async function updateSettings(settings: Settings): Promise<void> {
  try {
    // Save to localStorage
    if (typeof window !== "undefined") {
      const currentSettings = await getSettings();
      const updatedSettings = { ...currentSettings, ...settings };
      localStorage.setItem("userSettings", JSON.stringify(updatedSettings));
    }

    // In a real app, would also send to backend API
    // await fetch('/api/settings', {
    //     method: 'PUT',
    //     headers: { 'Content-Type': 'application/json' },
    //     body: JSON.stringify(settings),
    // });
  } catch (error) {
    console.error("Error updating settings:", error);
    throw error;
  }
}

/**
 * Validate settings before saving
 */
export async function validateSettings(settings: Settings): Promise<boolean> {
  try {
    // Validate theme
    if (
      settings.theme &&
      !["light", "dark", "system"].includes(settings.theme)
    ) {
      return false;
    }

    // Validate language
    if (
      settings.language &&
      !["en", "es", "fr", "de", "zh", "ja"].includes(settings.language)
    ) {
      return false;
    }

    // Validate password if provided
    if (settings.password && settings.password.length < 8) {
      return false;
    }

    return true;
  } catch (error) {
    console.error("Error validating settings:", error);
    return false;
  }
}

/**
 * Reset settings to defaults
 */
export async function resetSettings(): Promise<void> {
  try {
    if (typeof window !== "undefined") {
      localStorage.removeItem("userSettings");
    }
  } catch (error) {
    console.error("Error resetting settings:", error);
    throw error;
  }
}
