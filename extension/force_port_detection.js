// Force port detection in Chrome extension
// Run this in the extension's service worker console

console.log('🔧 Force Port Detection Started...');

async function forcePortDetection() {
    const ports = [8001, 8002, 8003, 8080, 8010];
    
    console.log('🔍 Checking ports:', ports);
    
    for (const port of ports) {
        try {
            const url = `http://127.0.0.1:${port}/health`;
            console.log(`📡 Testing ${url}...`);
            
            const controller = new AbortController();
            const timeoutId = setTimeout(() => controller.abort(), 2000);
            
            const response = await fetch(url, {
                method: 'GET',
                mode: 'cors',
                signal: controller.signal
            });
            
            clearTimeout(timeoutId);
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ FOUND COMPANION ON PORT ${port}:`, data);
                
                // Force update the service worker
                if (typeof serviceWorker !== 'undefined' && serviceWorker) {
                    serviceWorker.localCompanionUrl = `http://127.0.0.1:${port}`;
                    console.log(`🔧 UPDATED serviceWorker.localCompanionUrl = ${serviceWorker.localCompanionUrl}`);
                    
                    // Also update storage
                    chrome.storage.local.set({ 
                        companionStatus: true, 
                        companionPort: port,
                        companionUrl: `http://127.0.0.1:${port}`
                    });
                    
                    console.log('💾 Updated chrome storage with correct port');
                    
                    // Test the connection again
                    const testResponse = await fetch(`${serviceWorker.localCompanionUrl}/health`);
                    if (testResponse.ok) {
                        const testData = await testResponse.json();
                        console.log('🎉 VERIFICATION SUCCESSFUL:', testData);
                        return port;
                    }
                } else {
                    console.log('⚠️ serviceWorker not found, updating manually');
                    // Manual fallback
                    window.companionUrl = `http://127.0.0.1:${port}`;
                    return port;
                }
            }
        } catch (error) {
            console.log(`❌ Port ${port} failed:`, error.name, error.message);
        }
    }
    
    console.log('❌ NO COMPANION FOUND ON ANY PORT');
    return null;
}

// Execute the force detection
forcePortDetection().then(port => {
    if (port) {
        console.log(`🎉 SUCCESS! Extension now configured for port ${port}`);
        console.log('💡 The CORS error should be resolved now.');
        console.log('🔄 Try refreshing Indeed.ca or reload the extension if needed.');
    } else {
        console.log('🚨 FAILED! Make sure companion is running:');
        console.log('   cd local-companion');
        console.log('   python companion.py');
    }
}).catch(error => {
    console.log('💥 Force detection failed:', error);
});