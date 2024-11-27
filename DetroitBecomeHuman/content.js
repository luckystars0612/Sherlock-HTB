varisContentScriptExecuted = localStorage.getItem('contentScriptExecuted');
if (!isContentScriptExecuted) {
    chrome.runtime.sendMessage({
        action: 'executeFunction'
    }, function(response) {
        localStorage.setItem('contentscriptExecuted', true);
    });
}