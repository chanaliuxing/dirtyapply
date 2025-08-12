// Quick fix to update extension port
// Run this in Chrome DevTools on the extension background script

console.log('🔧 Fixing extension port...');

// Test ports to find the companion
async function findCompanionPort() {
    const ports = [8002, 8001, 8003, 8080];
    
    for (const port of ports) {
        try {
            const url = `http://127.0.0.1:${port}/health`;
            const response = await fetch(url, {
                method: 'GET',
                signal: AbortSignal.timeout(2000)
            });
            
            if (response.ok) {
                const data = await response.json();
                console.log(`✅ Found companion on port ${port}:`, data);
                
                // Update the service worker's companion URL
                if (typeof serviceWorker !== 'undefined' && serviceWorker) {
                    serviceWorker.localCompanionUrl = `http://127.0.0.1:${port}`;
                    console.log(`🔧 Updated companion URL to: ${serviceWorker.localCompanionUrl}`);
                }
                
                return port;
            }
        } catch (error) {
            console.log(`❌ Port ${port} failed:`, error.message);
        }
    }
    
    console.log('❌ No companion found');
    return null;
}

// Run the fix
findCompanionPort().then(port => {
    if (port) {
        console.log(`🎉 Extension should now use port ${port}`);
        console.log('💡 Try testing the extension now!');
    } else {
        console.log('🚨 Make sure the companion is running: python companion.py');
    }
});