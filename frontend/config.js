// Configuration for frontend applications
// Automatically detects if running locally or on a server

const Config = {
    // API URL configuration
    getApiUrl: function() {
        // Check if we're running on localhost or a development environment
        const hostname = window.location.hostname;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '') {
            return 'http://localhost:5000/api';
        }
        
        // For production, use relative URL or environment-specific URL
        return window.location.origin + '/api';
    },
    
    // WebSocket URL configuration
    getWebSocketUrl: function() {
        const hostname = window.location.hostname;
        
        if (hostname === 'localhost' || hostname === '127.0.0.1' || hostname === '') {
            return 'http://localhost:5000';
        }
        
        return window.location.origin;
    },
    
    // App settings
    settings: {
        autoRefreshInterval: 10000, // 10 seconds
        maxAlerts: 3, // Maximum alerts to show in UI
        webcamSettings: {
            width: 640,
            height: 480
        }
    }
};

// Export for use in HTML files
if (typeof module !== 'undefined' && module.exports) {
    module.exports = Config;
}
