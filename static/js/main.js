/**
 * Suikoden Display Web Interface - Main JavaScript
 * Handles WebSocket connections, UI interactions, and real-time updates
 */

// Initialize variables
let socket;
let allCharacters = [];
let currentParty = Array(6).fill(null);
let selectedCharacter = null;
let imageCache = {};
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY = 3000; // 3 seconds

// Cache DOM elements
const partyGrid = document.querySelector('.party-grid');
const starsContainer = document.getElementById('stars-container');
const searchInput = document.getElementById('star-search');
const characterImage = document.getElementById('selected-character-img');
const characterName = document.getElementById('selected-character-name');
const characterRecruitment = document.getElementById('selected-character-recruitment');

// DOM Ready event
document.addEventListener('DOMContentLoaded', () => {
    console.log('DOM loaded, initializing application...');
    
    // Show loading state initially
    showLoadingState(true);
    
    // Initial UI setup
    setupUI();
    
    // Set up event listeners
    setupEventListeners();
    
    // Initialize the Socket.IO connection
    initializeSocketConnection();
    
    // Remove any legacy polling that might have been added by browser extensions
    stopLegacyPolling();
});

/**
 * Initialize Socket.IO connection and event handlers
 */
function initializeSocketConnection() {
    // Enable debug logging for Socket.IO
    localStorage.debug = '*';
    console.log('Initializing Socket.IO connection...');
    
    // Create Socket.IO connection
    socket = io.connect(window.location.protocol + '//' + window.location.host, {
        reconnection: true,
        reconnectionAttempts: MAX_RECONNECT_ATTEMPTS,
        reconnectionDelay: RECONNECT_DELAY,
        timeout: 10000, // 10 seconds timeout
        autoConnect: true
    });
    
    // Socket connection established
    socket.on('connect', () => {
        console.log('Connected to server');
        reconnectAttempts = 0;
        
        // Show loading state
        showLoadingState(true);
        
        // Request initial data
        socket.emit('request_initial_data');
        
        // Show connected status
        showConnectionStatus(true);
        
        // Log connection details
        console.log('Socket ID:', socket.id);
        console.log('Socket connected:', socket.connected);
    });
    
    // Socket connection error
    socket.on('connect_error', (error) => {
        console.error('Connection error:', error);
        reconnectAttempts++;
        showConnectionStatus(false, `Connection error (attempt ${reconnectAttempts}/${MAX_RECONNECT_ATTEMPTS})`);
    });
    
    // Socket disconnected
    socket.on('disconnect', (reason) => {
        console.log('Disconnected:', reason);
        showConnectionStatus(false, 'Disconnected from server');
    });
    
    // Socket attempting to reconnect
    socket.on('reconnecting', (attemptNumber) => {
        console.log(`Attempting to reconnect (${attemptNumber}/${MAX_RECONNECT_ATTEMPTS})...`);
        showConnectionStatus(false, `Reconnecting (attempt ${attemptNumber}/${MAX_RECONNECT_ATTEMPTS})...`);
    });
    
    // Initial data received
    socket.on('initial_data', (data) => {
        console.log('Received initial data:', data);
        handleInitialData(data);
        showLoadingState(false);
    });
    
    // Server info messages
    socket.on('server_info', (data) => {
        console.log('Server info:', data.message);
        showToast(data.message, 'info');
    });
    
    // Party updated event
    socket.on('party_updated', (data) => {
        // Check if we have complete party data
        if (data.party) {
            updatePartyDisplay(data.party);
            
            // Show appropriate notification based on the action
            if (data.action === 'add') {
                showToast(`${data.character.name} added to party`, 'success');
            } else if (data.action === 'remove') {
                showToast(`${data.character_name} removed from party`, 'info');
            } else if (data.action === 'move') {
                showToast(`${data.character_name} moved in party`, 'info');
            } else if (data.action === 'full_update') {
                showToast('Party synchronized from external update', 'info');
            }
            
            // Store the updated party data
            currentParty = data.party;
            
            // Update the Stars list to reflect recruited status
            updateStarsList();
        } else {
            console.error('Received party_updated event without party data');
        }
    });
    
    // Character selected event
    socket.on('character_selected', (data) => {
        displayCharacterDetails(data.character, data.recruitment_info);
    });
    
    // Error handling for server errors
    socket.on('server_error', (data) => {
        console.error('Server error:', data.message);
        showToast(`Error: ${data.message}`, 'error');
    });
    
    // Socket.IO error event
    socket.on('error', (error) => {
        console.error('Socket.IO error:', error);
        showToast(`Connection error: ${error.message || 'Unknown error'}`, 'error');
    });
    
    // Success message for updates
    socket.on('update_success', (data) => {
        showToast(data.message, 'success');
    });
    
    // All characters list updated
    socket.on('all_characters_updated', (data) => {
        allCharacters = data.characters;
        updateStarsList();
    });
}

/**
 * Set up event listeners for user interactions
 */
function setupEventListeners() {
    // Search input for filtering characters
    searchInput.addEventListener('input', (e) => {
        const searchTerm = e.target.value.toLowerCase();
        filterCharacters(searchTerm);
    });
    
    // Clear search button if implemented
    const clearSearchBtn = document.querySelector('.clear-search');
    if (clearSearchBtn) {
        clearSearchBtn.addEventListener('click', () => {
            searchInput.value = '';
            filterCharacters('');
        });
    }
    
    // Add event listener for manual sync button if present
    const syncButton = document.getElementById('sync-party-button');
    if (syncButton) {
        syncButton.addEventListener('click', () => {
            syncPartyToServer();
        });
    }
}

/**
 * Initial UI setup
 */
function setupUI() {
    // Create empty party slots
    for (let i = 0; i < 6; i++) {
        const partySlot = document.querySelector(`.party-slot[data-position="${i}"]`);
        if (partySlot) {
            partySlot.addEventListener('click', () => selectPartySlot(i));
        }
    }
    
    // Show loading state while waiting for initial data
    showLoadingState(true);
}

/**
 * Update the party display with new party data
 */
function updatePartyDisplay(party) {
    // Ensure party data is valid
    if (!party || !Array.isArray(party) || party.length !== 6) {
        console.error('Invalid party data:', party);
        showToast('Invalid party data received', 'error');
        return;
    }
    
    currentParty = party;
    
    // Update each party slot with character data
    for (let i = 0; i < 6; i++) {
        const partySlot = document.querySelector(`.party-slot[data-position="${i}"]`);
        if (!partySlot) continue;
        
        // Remove empty class if present
        partySlot.classList.remove('empty');
        
        const memberData = party[i];
        
        // Check if slot has a character
        if (memberData) {
            let partyMember = partySlot.querySelector('.party-member');
            if (!partyMember) {
                partyMember = document.createElement('div');
                partyMember.className = 'party-member';
                
                const img = document.createElement('img');
                img.alt = memberData.name;
                img.onerror = () => { img.src = '/static/img/placeholder.png'; };
                
                const nameElem = document.createElement('div');
                nameElem.className = 'party-member-name';
                
                partyMember.appendChild(img);
                partyMember.appendChild(nameElem);
                
                // Clear existing content and add new member
                partySlot.innerHTML = '';
                partySlot.appendChild(partyMember);
            }
            
            // Update image and name
            const img = partyMember.querySelector('img');
            img.src = memberData.image_url;
            
            const nameElem = partyMember.querySelector('.party-member-name');
            nameElem.textContent = memberData.name;
        } else {
            // Empty slot
            partySlot.classList.add('empty');
            partySlot.innerHTML = '<div class="empty-text">Empty</div>';
        }
    }
    
    // Update stars list to reflect changes in recruitment status
    updateStarsList();
}

/**
 * Handle initial data received from server
 */
function handleInitialData(data) {
    try {
        // Process all characters
        if (data.characters && Array.isArray(data.characters)) {
            allCharacters = data.characters;
            console.log(`Loaded ${allCharacters.length} characters`);
        } else {
            console.error('Invalid characters data format:', data.characters);
            showToast('Error loading characters data', 'error');
            allCharacters = [];
        }
        
        // Update party if provided
        if (data.party && Array.isArray(data.party)) {
            updatePartyDisplay(data.party);
            console.log('Party data loaded successfully');
        } else {
            console.error('Invalid party data format:', data.party);
            showToast('Error loading party data', 'error');
        }
        
        // Update stars list
        updateStarsList();
        
        // Hide loading state
        showLoadingState(false);
        
        // Show success message
        showToast('Data loaded successfully', 'success');
    } catch (error) {
        console.error('Error handling initial data:', error);
        showToast('Error processing data: ' + error.message, 'error');
        showLoadingState(false);
    }
}

/**
 * Update the 108 Stars list display
 */
function updateStarsList() {
    if (!allCharacters || allCharacters.length === 0) {
        starsContainer.innerHTML = '<p>No character data available</p>';
        return;
    }
    
    // Clear current list
    starsContainer.innerHTML = '';
    
    // Group characters alphabetically
    const groupedCharacters = groupCharactersAlphabetically(allCharacters);
    
    // Create DOM elements for each group
    Object.keys(groupedCharacters).sort().forEach(letter => {
        // Create letter category header
        const categoryHeader = document.createElement('div');
        categoryHeader.className = 'stars-category';
        categoryHeader.textContent = letter;
        starsContainer.appendChild(categoryHeader);
        
        // Add divider
        const divider = document.createElement('div');
        divider.className = 'star-divider';
        starsContainer.appendChild(divider);
        
        // Add characters in this category
        groupedCharacters[letter].forEach(character => {
            const characterElement = document.createElement('div');
            characterElement.className = 'star-name';
            characterElement.textContent = character.name;
            
            // Add recruited class if character is in the party
            const isInParty = currentParty.some(member => member && member.name === character.name);
            if (isInParty) {
                characterElement.classList.add('recruited');
            }
            
            // Add click handler
            characterElement.addEventListener('click', () => {
                selectCharacter(character);
            });
            
            starsContainer.appendChild(characterElement);
        });
    });
}

/**
 * Group characters alphabetically
 */
function groupCharactersAlphabetically(characters) {
    const grouped = {};
    
    characters.forEach(character => {
        const firstLetter = character.name.charAt(0).toUpperCase();
        if (!grouped[firstLetter]) {
            grouped[firstLetter] = [];
        }
        grouped[firstLetter].push(character);
    });
    
    // Sort characters within each group
    Object.keys(grouped).forEach(letter => {
        grouped[letter].sort((a, b) => a.name.localeCompare(b.name));
    });
    
    return grouped;
}

/**
 * Filter characters based on search term
 */
function filterCharacters(searchTerm) {
    if (!allCharacters) return;
    
    // If empty search, show all characters
    if (!searchTerm) {
        updateStarsList();
        return;
    }
    
    // Filter characters that match the search term
    const filteredCharacters = allCharacters.filter(character => 
        character.name.toLowerCase().includes(searchTerm) ||
        (character.role && character.role.toLowerCase().includes(searchTerm))
    );
    
    // Create temporary characters array for display
    const tempCharacters = [...filteredCharacters];
    
    // Update the display with filtered results
    starsContainer.innerHTML = '';
    
    if (filteredCharacters.length === 0) {
        starsContainer.innerHTML = '<p class="no-results">No characters found matching "' + searchTerm + '"</p>';
        return;
    }
    
    // Group and display the filtered characters
    const groupedCharacters = groupCharactersAlphabetically(tempCharacters);
    
    // Create DOM elements for each group
    Object.keys(groupedCharacters).sort().forEach(letter => {
        // Create letter category header
        const categoryHeader = document.createElement('div');
        categoryHeader.className = 'stars-category';
        categoryHeader.textContent = letter;
        starsContainer.appendChild(categoryHeader);
        
        // Add divider
        const divider = document.createElement('div');
        divider.className = 'star-divider';
        starsContainer.appendChild(divider);
        
        // Add characters in this category
        groupedCharacters[letter].forEach(character => {
            const characterElement = document.createElement('div');
            characterElement.className = 'star-name';
            characterElement.textContent = character.name;
            
            // Add recruited class if character is in the party
            const isInParty = currentParty.some(member => member && member.name === character.name);
            if (isInParty) {
                characterElement.classList.add('recruited');
            }
            
            // Add click handler
            characterElement.addEventListener('click', () => {
                selectCharacter(character);
            });
            
            starsContainer.appendChild(characterElement);
        });
    });
}

/**
 * Handle character selection
 */
function selectCharacter(character) {
    selectedCharacter = character;
    
    // Update UI to show selected character
    const starNames = document.querySelectorAll('.star-name');
    starNames.forEach(element => {
        element.classList.remove('selected');
        if (element.textContent === character.name) {
            element.classList.add('selected');
        }
    });
    // Emit character selection to server
    socket.emit('select_character', { character_name: character.name });
    
    // Update character details display directly as well
    displayCharacterDetails(character, character.recruitment_info);
    
    // Show visual feedback
    showToast(`Selected ${character.name}`, 'info');
}

/**
 * Display character details in the recruitment panel
 */
function displayCharacterDetails(character, recruitmentInfo) {
    if (!character) return;
    
    // Update character name
    characterName.textContent = character.name;
    
    // Update character image
    if (character.image_url) {
        characterImage.src = character.image_url;
        characterImage.alt = character.name;
        
        // Handle image loading error
        characterImage.onerror = () => {
            characterImage.src = '/static/img/placeholder.png';
        };
    } else {
        characterImage.src = '/static/img/placeholder.png';
    }
    
    // Update recruitment information
    if (recruitmentInfo) {
        characterRecruitment.textContent = recruitmentInfo;
    } else {
        characterRecruitment.textContent = 'No recruitment information available.';
    }
}

/**
 * Handle party slot selection
 */
function selectPartySlot(slotIndex) {
    if (selectedCharacter) {
        // Check if character is already in party
        const existingSlot = currentParty.findIndex(member => 
            member && member.name === selectedCharacter.name
        );
        
        if (existingSlot !== -1 && existingSlot !== slotIndex) {
            // Character is already in another slot
            if (confirm(`${selectedCharacter.name} is already in the party. Move to slot ${slotIndex + 1}?`)) {
                try {
                    socket.emit('move_character', {
                        character_name: selectedCharacter.name,
                        from_slot: existingSlot,
                        to_slot: slotIndex
                    });
                    
                    // Provide immediate feedback
                    showToast(`Moving ${selectedCharacter.name}...`, 'info');
                } catch (error) {
                    console.error('Error moving character:', error);
                    showToast(`Failed to move character: ${error.message}`, 'error');
                }
            }
        } else if (existingSlot !== slotIndex) {
            // Add character to the selected slot
            try {
                socket.emit('add_to_party', {
                    character_name: selectedCharacter.name,
                    slot: slotIndex
                });
                
                // Provide immediate feedback
                showToast(`Adding ${selectedCharacter.name}...`, 'info');
            } catch (error) {
                console.error('Error adding character:', error);
                showToast(`Failed to add character: ${error.message}`, 'error');
            }
        }
    } else {
        // No character selected, check if we're trying to remove someone
        if (currentParty[slotIndex]) {
            // Slot has character - ask if user wants to remove
            if (confirm(`Remove ${currentParty[slotIndex].name} from the party?`)) {
                try {
                    socket.emit('remove_from_party', { slot: slotIndex });
                    
                    // Provide immediate feedback
                    showToast(`Removing ${currentParty[slotIndex].name}...`, 'info');
                } catch (error) {
                    console.error('Error removing character:', error);
                    showToast(`Failed to remove character: ${error.message}`, 'error');
                }
            }
        } else {
            // Show message to select a character first
            showToast('Please select a character from the 108 Stars list first.', 'warning');
        }
    }
}
/**
 * Show loading state while data is being fetched
 */
function showLoadingState(isLoading) {
    const loadingIndicator = document.querySelector('.loading-indicator');
    
    if (!loadingIndicator && isLoading) {
        // Create loading indicator if it doesn't exist
        const loadingElement = document.createElement('div');
        loadingElement.className = 'loading-indicator';
        loadingElement.innerHTML = `
            <div class="spinner"></div>
            <p>Loading Suikoden data...</p>
        `;
        document.body.appendChild(loadingElement);
        console.log('Loading state shown');
    } else if (loadingIndicator) {
        // Remove or hide existing loading indicator
        if (isLoading) {
            loadingIndicator.style.display = 'flex';
            console.log('Loading state shown');
        } else {
            loadingIndicator.style.display = 'none';
            console.log('Loading state hidden');
            setTimeout(() => {
                if (loadingIndicator.parentNode) {
                    loadingIndicator.parentNode.removeChild(loadingIndicator);
                }
            }, 500);
        }
    }
}

/**
 * Show connection status
 */
function showConnectionStatus(isConnected, message = null) {
    // Create or get the status container
    let statusContainer = document.getElementById('connection-status');
    
    if (!statusContainer) {
        statusContainer = document.createElement('div');
        statusContainer.id = 'connection-status';
        document.body.appendChild(statusContainer);
    }
    
    // Clear any existing status messages
    clearTimeout(statusContainer.timeout);
    
    // Set the appropriate class based on connection status
    statusContainer.className = isConnected ? 'connected' : 'disconnected';
    
    // Set the message
    if (message) {
        statusContainer.textContent = message;
    } else {
        statusContainer.textContent = isConnected ? 'Connected to server' : 'Disconnected from server';
    }
    
    // Show the status
    statusContainer.style.display = 'block';
    
    // Auto-hide connected status after 3 seconds, keep error messages visible
    if (isConnected) {
        statusContainer.timeout = setTimeout(() => {
            statusContainer.style.display = 'none';
        }, 3000);
    }
}

/**
 * Show a toast notification
 */
function showToast(message, type = 'info', duration = 3000) {
    // Create toast container if it doesn't exist
    let toastContainer = document.querySelector('.toast-container');
    if (!toastContainer) {
        toastContainer = document.createElement('div');
        toastContainer.className = 'toast-container';
        document.body.appendChild(toastContainer);
    }
    
    // Create the toast
    const toast = document.createElement('div');
    toast.className = `toast ${type}`;
    toast.textContent = message;
    
    // Add to container
    toastContainer.appendChild(toast);
    
    // Trigger animation
    setTimeout(() => {
        toast.classList.add('show');
    }, 10);
    
    // Auto-remove after duration
    setTimeout(() => {
        toast.classList.remove('show');
        toast.classList.add('hide');
        
        // Remove from DOM after animation completes
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    }, duration);
    
    // Add click to dismiss
    toast.addEventListener('click', () => {
        toast.classList.remove('show');
        toast.classList.add('hide');
        setTimeout(() => {
            if (toast.parentNode) {
                toast.parentNode.removeChild(toast);
            }
        }, 300);
    });
}
/**
 * Handle server errors
 */
function handleServerError(error) {
    console.error('Server error:', error);
    showToast('Error: ' + (error.message || 'An unexpected error occurred'), 'error');
}

/**
 * Send party update to server to synchronize external changes
 */
function syncPartyToServer() {
    try {
        socket.emit('external_party_update', {
            party: currentParty,
            source: 'ui'
        });
    } catch (error) {
        console.error('Error syncing party to server:', error);
        showToast(`Failed to sync party data: ${error.message}`, 'error');
    }
}

// Add a function to handle external party updates
function handleExternalPartyUpdate(partyData) {
    // Update local party data
    if (partyData && Array.isArray(partyData)) {
        currentParty = partyData;
        updatePartyDisplay(currentParty);
        showToast('Party synchronized from external source', 'info');
    } else {
        console.error('Invalid external party data format:', partyData);
    }
}

// Add error handler for global socket errors
window.addEventListener('load', () => {
    window.addEventListener('error', (event) => {
        console.error('Global error:', event.error);
        showToast('Application error: ' + (event.error?.message || 'An unexpected error occurred'), 'error');
    });
    
    // Initialize any other components
    initializeAnimations();
});

/**
 * Initialize animations for UI elements
 */
function initializeAnimations() {
    // Add animation classes to elements when they come into view
    const animatedElements = document.querySelectorAll('.animate-on-view');
    
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('animated');
                observer.unobserve(entry.target);
            }
        });
    }, { threshold: 0.1 });
    
    animatedElements.forEach(element => {
        observer.observe(element);
    });
    
    // Add hover effects for interactive elements
    const interactiveElements = document.querySelectorAll('.star-name, .party-slot:not(.empty)');
    interactiveElements.forEach(element => {
        element.classList.add('with-hover-effect');
    });
}

/**
 * Stop any legacy polling mechanisms that might have been added
 */
function stopLegacyPolling() {
    // Clear all existing intervals to stop polling
    const maxIntervalId = window.setInterval(function(){}, 0);
    for (let i = 1; i <= maxIntervalId; i++) {
        window.clearInterval(i);
    }
    
    // Clear intervals and timeouts from the window object
    if (window._pollingIntervals) {
        window._pollingIntervals.forEach(interval => clearInterval(interval));
        window._pollingIntervals = [];
    }
    
    // Monkey patch fetch and XMLHttpRequest to block /get_data requests
    const originalFetch = window.fetch;
    window.fetch = function(url, options) {
        if (typeof url === 'string' && url.includes('/get_data')) {
            console.warn('Blocked legacy fetch request to /get_data');
            return Promise.reject(new Error('Legacy endpoint disabled'));
        }
        return originalFetch.apply(this, arguments);
    };
    
    const originalOpen = XMLHttpRequest.prototype.open;
    XMLHttpRequest.prototype.open = function(method, url, async, user, password) {
        if (typeof url === 'string' && url.includes('/get_data')) {
            console.warn('Blocked legacy XHR request to /get_data');
            throw new Error('Legacy endpoint disabled');
        }
        return originalOpen.apply(this, arguments);
    };
    
    console.log('Stopped any potential legacy polling mechanisms');
}
