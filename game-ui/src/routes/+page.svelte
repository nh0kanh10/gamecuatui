<script lang="ts">
    import { onMount } from 'svelte';
    import { game, type GameState } from '$lib/game';
    import { Send, Scroll, Backpack, HelpCircle, RotateCcw, MapPin, Heart, User } from 'lucide-svelte';

    let gameState: GameState = game.state;
    let userInput = '';
    let isLoading = false;
    let chatContainer: HTMLElement;

    async function handleSubmit() {
        if (!userInput.trim() || isLoading) return;
        
        const input = userInput;
        userInput = '';
        isLoading = true;

        // Update UI immediately for user message
        gameState = { ...game.state }; 
        scrollToBottom();

        await game.generateResponse(input);
        
        // Update UI with AI response
        gameState = { ...game.state };
        isLoading = false;
        scrollToBottom();
    }

    function scrollToBottom() {
        setTimeout(() => {
            if (chatContainer) {
                chatContainer.scrollTop = chatContainer.scrollHeight;
            }
        }, 50);
    }

    function handleQuickAction(action: string) {
        userInput = action;
        handleSubmit();
    }

    onMount(() => {
        // Initial welcome message if empty
        if (gameState.history.length === 0) {
            game.state.history.push({
                role: 'assistant',
                content: "Welcome, brave adventurer! You stand at the entrance of an ancient dungeon. The air is thick with mystery. What will you do?",
                timestamp: new Date()
            });
            gameState = { ...game.state };
        }
    });
</script>

<div class="min-h-screen bg-background text-foreground p-6 flex gap-6 max-w-7xl mx-auto font-sans">
    
    <!-- LEFT SIDEBAR: STATS -->
    <div class="w-80 flex flex-col gap-6">
        <!-- Character Card -->
        <div class="bg-card border border-border rounded-xl p-5 shadow-lg">
            <div class="flex items-center gap-3 mb-4">
                <div class="p-2 bg-primary/10 rounded-lg">
                    <User class="w-6 h-6 text-primary" />
                </div>
                <div>
                    <h2 class="font-bold text-lg">{gameState.playerName}</h2>
                    <p class="text-xs text-muted-foreground">Level 1 Adventurer</p>
                </div>
            </div>

            <div class="space-y-4">
                <!-- HP -->
                <div>
                    <div class="flex justify-between text-sm mb-1">
                        <span class="text-muted-foreground flex items-center gap-1"><Heart class="w-3 h-3" /> Health</span>
                        <span class="font-bold">{gameState.hp} / {gameState.maxHp}</span>
                    </div>
                    <div class="h-2 bg-secondary rounded-full overflow-hidden">
                        <div class="h-full bg-red-500 transition-all duration-500" style="width: {(gameState.hp / gameState.maxHp) * 100}%"></div>
                    </div>
                </div>

                <!-- Location -->
                <div class="p-3 bg-secondary/30 rounded-lg border border-border/50">
                    <div class="text-xs text-muted-foreground uppercase tracking-wider mb-1 flex items-center gap-1">
                        <MapPin class="w-3 h-3" /> Location
                    </div>
                    <div class="font-medium text-primary">{gameState.location}</div>
                </div>
            </div>
        </div>

        <!-- Inventory Card -->
        <div class="bg-card border border-border rounded-xl p-5 shadow-lg flex-1">
            <h3 class="font-bold text-sm uppercase tracking-wider text-muted-foreground mb-4 flex items-center gap-2">
                <Backpack class="w-4 h-4" /> Inventory
            </h3>
            <div class="flex flex-wrap gap-2">
                {#each gameState.inventory as item}
                    <span class="px-3 py-1.5 bg-secondary text-secondary-foreground rounded-md text-sm border border-border/50 hover:bg-secondary/80 transition-colors cursor-default">
                        {item}
                    </span>
                {/each}
            </div>
        </div>
    </div>

    <!-- MAIN CHAT AREA -->
    <div class="flex-1 flex flex-col bg-card border border-border rounded-xl shadow-xl overflow-hidden">
        <!-- Header -->
        <div class="p-4 border-b border-border bg-card/50 backdrop-blur flex justify-between items-center">
            <h1 class="font-bold text-xl flex items-center gap-2">
                <Scroll class="w-5 h-5 text-primary" />
                Text Adventure
            </h1>
            <div class="text-xs px-2 py-1 bg-green-500/10 text-green-500 rounded border border-green-500/20">
                Online: {game.model}
            </div>
        </div>

        <!-- Chat History -->
        <div class="flex-1 overflow-y-auto p-6 space-y-6 scroll-smooth" bind:this={chatContainer}>
            {#each gameState.history as msg}
                <div class="flex flex-col {msg.role === 'user' ? 'items-end' : 'items-start'}">
                    <div class="max-w-[80%] rounded-2xl p-4 {msg.role === 'user' ? 'bg-primary text-primary-foreground rounded-tr-none' : 'bg-secondary text-secondary-foreground rounded-tl-none'} shadow-sm">
                        <p class="leading-relaxed whitespace-pre-wrap">{msg.content}</p>
                    </div>
                    <span class="text-[10px] text-muted-foreground mt-1 px-2">
                        {msg.role === 'user' ? 'You' : 'Game Master'} • {msg.timestamp.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'})}
                    </span>
                </div>
            {/each}

            {#if isLoading}
                <div class="flex items-start">
                    <div class="bg-secondary/50 text-secondary-foreground rounded-2xl rounded-tl-none p-4 flex gap-1 items-center">
                        <div class="w-2 h-2 bg-primary/50 rounded-full animate-bounce"></div>
                        <div class="w-2 h-2 bg-primary/50 rounded-full animate-bounce delay-75"></div>
                        <div class="w-2 h-2 bg-primary/50 rounded-full animate-bounce delay-150"></div>
                    </div>
                </div>
            {/if}
        </div>

        <!-- Input Area -->
        <div class="p-4 border-t border-border bg-background/50 backdrop-blur">
            <!-- Quick Actions -->
            <div class="flex gap-2 mb-4 overflow-x-auto pb-2">
                <button on:click={() => handleQuickAction('Look around')} class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-secondary hover:bg-secondary/80 rounded-full transition-colors border border-border">
                    <MapPin class="w-3 h-3" /> Look around
                </button>
                <button on:click={() => handleQuickAction('Check inventory')} class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-secondary hover:bg-secondary/80 rounded-full transition-colors border border-border">
                    <Backpack class="w-3 h-3" /> Inventory
                </button>
                <button on:click={() => handleQuickAction('Help')} class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-secondary hover:bg-secondary/80 rounded-full transition-colors border border-border">
                    <HelpCircle class="w-3 h-3" /> Help
                </button>
                <button on:click={() => game.reset()} class="flex items-center gap-1.5 px-3 py-1.5 text-xs font-medium bg-red-500/10 text-red-500 hover:bg-red-500/20 rounded-full transition-colors border border-red-500/20 ml-auto">
                    <RotateCcw class="w-3 h-3" /> Reset
                </button>
            </div>

            <!-- Text Input -->
            <form on:submit|preventDefault={handleSubmit} class="flex gap-3">
                <input 
                    type="text" 
                    bind:value={userInput}
                    placeholder="What do you want to do?"
                    class="flex-1 bg-background border border-border rounded-xl px-4 py-3 focus:outline-none focus:ring-2 focus:ring-primary/50 transition-all placeholder:text-muted-foreground/50"
                    disabled={isLoading}
                />
                <button 
                    type="submit" 
                    disabled={!userInput.trim() || isLoading}
                    class="bg-primary text-primary-foreground p-3 rounded-xl hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-lg shadow-primary/20"
                >
                    <Send class="w-5 h-5" />
                </button>
            </form>
        </div>
    </div>
</div>
