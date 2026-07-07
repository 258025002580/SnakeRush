// Constants
const WINDOW_WIDTH = 900;
const WINDOW_HEIGHT = 700;
const GRID_SIZE = 25;
const GRID_WIDTH = Math.floor(WINDOW_WIDTH / GRID_SIZE);
const GRID_HEIGHT = Math.floor((WINDOW_HEIGHT - 100) / GRID_SIZE);
const FPS = 8;
const FRAME_TIME = 1000 / FPS;

// Colors
const BLACK = '#000000';
const WHITE = '#ffffff';
const DARK_BG = '#0f1423';
const GRID_LINE = '#192338';
const SNAKE_HEAD = '#00e6b4';
const SNAKE_BODY = '#00b48c';
const SNAKE_TAIL = '#008c6e';
const FOOD_COLOR = '#ff5050';
const FOOD_GLOW = '#ff7878';
const GOLD = '#ffd700';
const DARK_GRAY = '#283452';
const LIGHT_GRAY = '#b4c3dc';
const MENU_BG = '#142032';
const BUTTON_COLOR = '#00c8a0';
const BUTTON_HOVER = '#00e6b4';

// Game States
const GameState = {
    MENU: 0,
    PLAYING: 1,
    PAUSED: 2,
    GAME_OVER: 3
};

// Directions
const Direction = {
    UP: { x: 0, y: -1 },
    DOWN: { x: 0, y: 1 },
    LEFT: { x: -1, y: 0 },
    RIGHT: { x: 1, y: 0 }
};

// DOM Elements
let canvas, ctx;
let menuOverlay, pauseOverlay, gameOverOverlay;
let startButton, restartButton, menuButton;
let scoreDisplay, highScorePanel, lengthDisplay, highscoreDisplay, finalScoreDisplay, newRecordDisplay;

class SnakeGame {
    constructor() {
        this.state = GameState.MENU;
        this.snake = [];
        this.direction = Direction.RIGHT;
        this.nextDirection = Direction.RIGHT;
        this.score = 0;
        this.highScore = this.loadHighScore();
        this.food = { x: 0, y: 0 };
        this.animationFrame = 0;
        this.shakeOffset = { x: 0, y: 0 };
        this.lastUpdateTime = 0;
        this.setupCanvas();
        this.setupUI();
        this.setupEventListeners();
        this.resetGame();
        this.updateUI();
        this.draw();
    }

    setupCanvas() {
        canvas = document.getElementById('gameCanvas');
        ctx = canvas.getContext('2d');
    }

    setupUI() {
        menuOverlay = document.getElementById('menuOverlay');
        pauseOverlay = document.getElementById('pauseOverlay');
        gameOverOverlay = document.getElementById('gameOverOverlay');
        startButton = document.getElementById('startButton');
        restartButton = document.getElementById('restartButton');
        menuButton = document.getElementById('menuButton');
        scoreDisplay = document.getElementById('scoreDisplay');
        highScorePanel = document.getElementById('highScorePanel');
        lengthDisplay = document.getElementById('lengthDisplay');
        highscoreDisplay = document.getElementById('highscoreDisplay');
        finalScoreDisplay = document.getElementById('finalScore');
        newRecordDisplay = document.getElementById('newRecord');
    }

    setupEventListeners() {
        document.addEventListener('keydown', (e) => this.handleKeyDown(e));
        startButton.addEventListener('click', () => this.startGame());
        restartButton.addEventListener('click', () => this.startGame());
        menuButton.addEventListener('click', () => this.goToMenu());
    }

    handleKeyDown(e) {
        switch (this.state) {
            case GameState.MENU:
                if (e.key === 'Enter' || e.key === ' ') {
                    this.startGame();
                }
                break;
            case GameState.PLAYING:
                if (e.key === 'Escape' || e.key === 'p' || e.key === 'P') {
                    this.state = GameState.PAUSED;
                    this.updateUI();
                } else {
                    this.changeDirection(e.key);
                }
                break;
            case GameState.PAUSED:
                if (e.key === 'Escape' || e.key === 'p' || e.key === 'P') {
                    this.state = GameState.PLAYING;
                    this.updateUI();
                }
                break;
            case GameState.GAME_OVER:
                if (e.key === 'Enter' || e.key === ' ') {
                    this.startGame();
                } else if (e.key === 'Escape') {
                    this.goToMenu();
                }
                break;
        }
    }

    changeDirection(key) {
        const current = this.direction;
        if ((key === 'ArrowUp' || key === 'w' || key === 'W') && current !== Direction.DOWN) {
            this.nextDirection = Direction.UP;
        } else if ((key === 'ArrowDown' || key === 's' || key === 'S') && current !== Direction.UP) {
            this.nextDirection = Direction.DOWN;
        } else if ((key === 'ArrowLeft' || key === 'a' || key === 'A') && current !== Direction.RIGHT) {
            this.nextDirection = Direction.LEFT;
        } else if ((key === 'ArrowRight' || key === 'd' || key === 'D') && current !== Direction.LEFT) {
            this.nextDirection = Direction.RIGHT;
        }
    }

    resetGame() {
        const startX = Math.floor(GRID_WIDTH / 2);
        const startY = Math.floor(GRID_HEIGHT / 2);
        this.snake = [
            { x: startX, y: startY },
            { x: startX - 1, y: startY },
            { x: startX - 2, y: startY }
        ];
        this.direction = Direction.RIGHT;
        this.nextDirection = Direction.RIGHT;
        this.score = 0;
        this.food = this.spawnFood();
        this.animationFrame = 0;
        this.shakeOffset = { x: 0, y: 0 };
    }

    spawnFood() {
        while (true) {
            const x = Math.floor(Math.random() * GRID_WIDTH);
            const y = Math.floor(Math.random() * GRID_HEIGHT);
            let collision = false;
            for (const segment of this.snake) {
                if (segment.x === x && segment.y === y) {
                    collision = true;
                    break;
                }
            }
            if (!collision) {
                return { x, y };
            }
        }
    }

    loadHighScore() {
        const score = localStorage.getItem('snakeHighScore');
        return score ? parseInt(score, 10) : 0;
    }

    saveHighScore() {
        localStorage.setItem('snakeHighScore', this.highScore.toString());
    }

    update(currentTime) {
        // Shake decay
        this.shakeOffset.x *= 0.8;
        this.shakeOffset.y *= 0.8;
        if (Math.abs(this.shakeOffset.x) < 0.1) this.shakeOffset.x = 0;
        if (Math.abs(this.shakeOffset.y) < 0.1) this.shakeOffset.y = 0;

        if (this.state !== GameState.PLAYING) return;

        const delta = currentTime - this.lastUpdateTime;
        if (delta < FRAME_TIME) return;

        this.direction = this.nextDirection;
        const head = this.snake[0];
        const newHead = {
            x: head.x + this.direction.x,
            y: head.y + this.direction.y
        };

        // Wall collision
        if (newHead.x < 0 || newHead.x >= GRID_WIDTH ||
            newHead.y < 0 || newHead.y >= GRID_HEIGHT) {
            this.gameOver();
            return;
        }

        // Self collision
        for (const segment of this.snake) {
            if (segment.x === newHead.x && segment.y === newHead.y) {
                this.gameOver();
                return;
            }
        }

        this.snake.unshift(newHead);

        // Food collision
        if (newHead.x === this.food.x && newHead.y === this.food.y) {
            this.score += 10;
            this.food = this.spawnFood();
        } else {
            this.snake.pop();
        }

        this.animationFrame++;
        this.lastUpdateTime = currentTime;
        this.updateUI();
    }

    gameOver() {
        this.state = GameState.GAME_OVER;
        this.shakeOffset = {
            x: Math.floor(Math.random() * 11) - 5,
            y: Math.floor(Math.random() * 11) - 5
        };
        if (this.score > this.highScore) {
            this.highScore = this.score;
            this.saveHighScore();
            newRecordDisplay.style.display = 'block';
        } else {
            newRecordDisplay.style.display = 'none';
        }
        this.updateUI();
    }

    startGame() {
        this.resetGame();
        this.state = GameState.PLAYING;
        this.updateUI();
        this.lastUpdateTime = performance.now();
    }

    goToMenu() {
        this.state = GameState.MENU;
        this.updateUI();
    }

    updateUI() {
        // Update overlays visibility
        menuOverlay.style.display = this.state === GameState.MENU ? 'flex' : 'none';
        pauseOverlay.style.display = this.state === GameState.PAUSED ? 'flex' : 'none';
        gameOverOverlay.style.display = this.state === GameState.GAME_OVER ? 'flex' : 'none';

        // Update score displays
        scoreDisplay.textContent = this.score;
        highScorePanel.textContent = this.highScore;
        highscoreDisplay.textContent = this.highScore;
        lengthDisplay.textContent = this.snake.length;
        finalScoreDisplay.textContent = this.score;
    }

    draw() {
        ctx.clearRect(0, 0, WINDOW_WIDTH, WINDOW_HEIGHT);
        this.drawGrid();
        if (this.state === GameState.PLAYING) {
            this.drawSnake();
            this.drawFood();
        }
        // UI is separate HTML overlays, no need to draw here
    }

    drawGrid() {
        for (let x = 0; x < GRID_WIDTH; x++) {
            for (let y = 0; y < GRID_HEIGHT; y++) {
                const rectX = x * GRID_SIZE;
                const rectY = 100 + y * GRID_SIZE;
                ctx.fillStyle = (x + y) % 2 === 0 ? GRID_LINE : DARK_BG;
                ctx.fillRect(rectX, rectY, GRID_SIZE, GRID_SIZE);
                ctx.strokeStyle = GRID_LINE;
                ctx.strokeRect(rectX, rectY, GRID_SIZE, GRID_SIZE);
            }
        }
    }

    drawSnake() {
        for (let i = this.snake.length - 1; i >= 0; i--) {
            const segment = this.snake[i];
            const progress = i / (this.snake.length - 1 || 1);
            const color = this.lerpColor(SNAKE_HEAD, SNAKE_TAIL, 1 - progress);
            const centerX = segment.x * GRID_SIZE + GRID_SIZE / 2 + this.shakeOffset.x;
            const centerY = 100 + segment.y * GRID_SIZE + GRID_SIZE / 2 + this.shakeOffset.y;
            const radius = GRID_SIZE / 2 - 2;

            ctx.fillStyle = color;
            ctx.beginPath();
            ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
            ctx.fill();
            ctx.strokeStyle = WHITE;
            ctx.lineWidth = 2;
            ctx.stroke();

            if (i === 0) {
                this.drawSnakeHead(centerX, centerY, radius);
            }
        }
    }

    drawSnakeHead(centerX, centerY, radius) {
        const dx = this.direction.x;
        const dy = this.direction.y;
        const eyeOffset = radius / 3;
        const eyeSize = radius / 4;
        let eye1, eye2, pupilOffsetX = 0, pupilOffsetY = 0;

        if (dx === 1) {
            eye1 = { x: centerX + eyeOffset, y: centerY - eyeOffset };
            eye2 = { x: centerX + eyeOffset, y: centerY + eyeOffset };
            pupilOffsetX = eyeSize / 2;
        } else if (dx === -1) {
            eye1 = { x: centerX - eyeOffset, y: centerY - eyeOffset };
            eye2 = { x: centerX - eyeOffset, y: centerY + eyeOffset };
            pupilOffsetX = -eyeSize / 2;
        } else if (dy === -1) {
            eye1 = { x: centerX - eyeOffset, y: centerY - eyeOffset };
            eye2 = { x: centerX + eyeOffset, y: centerY - eyeOffset };
            pupilOffsetY = -eyeSize;
        } else {
            // dy === 1 (DOWN)
            eye1 = { x: centerX - eyeOffset, y: centerY + eyeOffset };
            eye2 = { x: centerX + eyeOffset, y: centerY + eyeOffset };
            pupilOffsetY = eyeSize;
        }

        [eye1, eye2].forEach(eye => {
            ctx.fillStyle = WHITE;
            ctx.beginPath();
            ctx.arc(eye.x, eye.y, eyeSize, 0, Math.PI * 2);
            ctx.fill();
            ctx.fillStyle = BLACK;
            ctx.beginPath();
            ctx.arc(eye.x + pupilOffsetX, eye.y + pupilOffsetY, eyeSize / 2, 0, Math.PI * 2);
            ctx.fill();
        });
    }

    drawFood() {
        const pulse = Math.sin(this.animationFrame * 0.1) * 3;
        const radius = GRID_SIZE / 2 - 2 + pulse;
        const centerX = this.food.x * GRID_SIZE + GRID_SIZE / 2 + this.shakeOffset.x;
        const centerY = 100 + this.food.y * GRID_SIZE + GRID_SIZE / 2 + this.shakeOffset.y;

        // Glow effect
        for (let glowRadius = radius + 8; glowRadius > radius; glowRadius -= 2) {
            const alpha = Math.floor(100 * (glowRadius - radius) / 8);
            ctx.fillStyle = `rgba(255, 120, 120, ${alpha / 100})`;
            ctx.beginPath();
            ctx.arc(centerX, centerY, glowRadius, 0, Math.PI * 2);
            ctx.fill();
        }

        ctx.fillStyle = FOOD_COLOR;
        ctx.beginPath();
        ctx.arc(centerX, centerY, radius, 0, Math.PI * 2);
        ctx.fill();
        ctx.strokeStyle = WHITE;
        ctx.lineWidth = 2;
        ctx.stroke();
    }

    lerpColor(color1, color2, t) {
        const r1 = parseInt(color1.slice(1, 3), 16);
        const g1 = parseInt(color1.slice(3, 5), 16);
        const b1 = parseInt(color1.slice(5, 7), 16);
        const r2 = parseInt(color2.slice(1, 3), 16);
        const g2 = parseInt(color2.slice(3, 5), 16);
        const b2 = parseInt(color2.slice(5, 7), 16);
        const r = Math.floor(r1 + (r2 - r1) * t);
        const g = Math.floor(g1 + (g2 - g1) * t);
        const b = Math.floor(b1 + (b2 - b1) * t);
        return `#${r.toString(16).padStart(2, '0')}${g.toString(16).padStart(2, '0')}${b.toString(16).padStart(2, '0')}`;
    }

    gameLoop(currentTime) {
        this.update(currentTime);
        this.draw();
        requestAnimationFrame((time) => this.gameLoop(time));
    }
}

// Initialize game when DOM is ready
window.addEventListener('DOMContentLoaded', () => {
    const game = new SnakeGame();
    requestAnimationFrame((time) => game.gameLoop(time));
});
