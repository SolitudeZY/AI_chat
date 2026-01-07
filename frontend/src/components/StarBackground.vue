<script setup>
import { onMounted, onUnmounted, ref } from 'vue';

const canvas = ref(null);
const container = ref(null);
let animationFrameId = null;

// Settings
let rotationSpeed = 0.025;
let fadeSpeed = 0.04;
let centerX = 50;
let centerY = 50;

let showContext = null;
let helpContext = null;
let helpCanvas = null;
let showWidth = 0;
let showHeight = 0;
let longSide = 0;
let drawTimes = 0;

// Helper functions
const rand = (Min, Max) => Min + Math.round(Math.random() * (Max - Min));

const colorThemes = [
    // Classic Rainbow
    () => {
        const r = rand(120, 255);
        const g = rand(120, 255);
        const b = rand(120, 255);
        const a = rand(30, 100) / 100;
        return `rgba(${r},${g},${b},${a})`;
    },
];

const randomColor = () => colorThemes[0]();

const createStar = (width, height) => {
    const size = Math.random() * 1 + 0.3;
    return {
        x: rand(-width, width),
        y: rand(-height, height),
        size: size,
        color: randomColor(),
        brightness: Math.random() * 0.5 + 0.5,
    };
};

const drawStars = (stars, ctx) => {
    let count = stars.length;
    while (count--) {
        const star = stars[count];
        
        // Radial gradient
        const gradient = ctx.createRadialGradient(
            star.x, star.y, 0,
            star.x, star.y, star.size * 3
        );
        gradient.addColorStop(0, star.color);
        gradient.addColorStop(0.5, star.color.replace(/[\d\.]+\)$/g, (star.brightness * 0.3) + ')'));
        gradient.addColorStop(1, 'rgba(0,0,0,0)');

        // Glow
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size * 3, 0, Math.PI * 2, true);
        ctx.fillStyle = gradient;
        ctx.fill();

        // Core
        ctx.beginPath();
        ctx.arc(star.x, star.y, star.size, 0, Math.PI * 2, true);
        ctx.fillStyle = star.color;
        ctx.shadowBlur = star.size * 1.5;
        ctx.shadowColor = star.color;
        ctx.fill();
        ctx.shadowBlur = 0;
    }
};

const updateCanvasTransform = () => {
    if (showContext && showWidth && showHeight) {
        const actualX = (centerX / 100) * showWidth;
        const actualY = (centerY / 100) * showHeight;
        
        showContext.setTransform(1, 0, 0, 1, 0, 0);
        showContext.translate(actualX, actualY);
    }
};

const init = () => {
    if (!canvas.value) return;

    showWidth = canvas.value.offsetWidth;
    showHeight = canvas.value.offsetHeight;
    canvas.value.width = showWidth;
    canvas.value.height = showHeight;

    // Create helper canvas
    helpCanvas = document.createElement('canvas');
    longSide = Math.max(showWidth, showHeight);
    helpCanvas.width = longSide * 2.6;
    helpCanvas.height = longSide * 2.6;

    showContext = canvas.value.getContext('2d');
    helpContext = helpCanvas.getContext('2d');

    // Initial background
    showContext.fillStyle = 'rgba(0,0,0,1)';
    showContext.fillRect(0, 0, showWidth, showHeight);

    // Create stars
    const stars = [];
    let count = 20000;
    while (count--) {
        stars.push(createStar(helpCanvas.width, helpCanvas.height));
    }

    // Draw stars on helper canvas
    drawStars(stars, helpContext);

    updateCanvasTransform();
    animate();
};

const loop = () => {
    if (!showContext || !helpCanvas) return;

    showContext.drawImage(helpCanvas, -helpCanvas.width / 2, -helpCanvas.height / 2);

    drawTimes++;

    if (drawTimes > 200 && drawTimes % 8 === 0) {
        showContext.fillStyle = `rgba(0,0,0,${fadeSpeed})`;
        showContext.fillRect(-(longSide * 3), -(longSide * 3), longSide * 6, longSide * 6);
    }
    
    showContext.rotate(rotationSpeed * Math.PI / 180);
};

const animate = () => {
    animationFrameId = requestAnimationFrame(animate);
    loop();
};

const resize = () => {
    if (canvas.value) {
        showWidth = window.innerWidth;
        showHeight = window.innerHeight;
        canvas.value.width = showWidth;
        canvas.value.height = showHeight;
        
        showContext.fillStyle = 'rgba(0,0,0,1)';
        showContext.fillRect(0, 0, showWidth, showHeight);
        
        updateCanvasTransform();
    }
};

onMounted(() => {
    window.addEventListener('resize', resize);
    // Delay init slightly to ensure container size is ready
    setTimeout(init, 100);
});

onUnmounted(() => {
    window.removeEventListener('resize', resize);
    cancelAnimationFrame(animationFrameId);
});
</script>

<template>
    <div class="fixed top-0 left-0 w-full h-full -z-10 bg-black overflow-hidden" ref="container">
        <!-- Background Stars (Twinkling) -->
        <div class="absolute top-0 left-0 w-full h-full pointer-events-none z-0">
             <div v-for="i in 50" :key="i" 
                  class="absolute rounded-full bg-white animate-twinkle"
                  :style="{
                      left: Math.random() * 100 + '%',
                      top: Math.random() * 100 + '%',
                      width: Math.random() * 2 + 1 + 'px',
                      height: Math.random() * 2 + 1 + 'px',
                      animationDelay: Math.random() * 3 + 's',
                      opacity: Math.random() * 0.7 + 0.3
                  }">
             </div>
        </div>
        
        <!-- Star Trails -->
        <canvas ref="canvas" class="w-full h-full block filter blur-[0.3px] brightness-110 relative z-10"></canvas>
        
        <!-- Vignette/Glow overlay -->
        <div class="absolute top-0 left-0 w-full h-full pointer-events-none z-20 bg-radial-glow"></div>
    </div>
</template>

<style scoped>
@keyframes twinkle {
    0%, 100% { opacity: 0.3; transform: scale(1); }
    50% { opacity: 1; transform: scale(1.2); }
}

.animate-twinkle {
    animation: twinkle 3s infinite;
}

.bg-radial-glow {
    background: radial-gradient(circle at 50% 50%, rgba(100, 149, 237, 0.1) 0%, transparent 50%);
}
</style>
