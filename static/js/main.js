const scene = new THREE.Scene();
const camera = new THREE.PerspectiveCamera(75, window.innerWidth / window.innerHeight, 0.1, 1000);
const renderer = new THREE.WebGLRenderer({ alpha: true });

renderer.setSize(window.innerWidth, window.innerHeight);
document.getElementById('canvas-container').appendChild(renderer.domElement);

const geometry = new THREE.BufferGeometry();
const particlesCount = 700;
const posArray = new Float32Array(particlesCount * 3);

for(let i = 0; i < particlesCount * 3; i++) {
    posArray[i] = (Math.random() - 0.5) * 15;
}

geometry.setAttribute('position', new THREE.BufferAttribute(posArray, 3));

// Material
const material = new THREE.PointsMaterial({
    size: 0.02,
    color: 0x00f2ff, 
    transparent: true,
    opacity: 0.8,
});


const particlesMesh = new THREE.Points(geometry, material);
scene.add(particlesMesh);

camera.position.z = 3;


let mouseX = 0;
let mouseY = 0;

document.addEventListener('mousemove', (event) => {
    mouseX = event.clientX;
    mouseY = event.clientY;
});

// Animation Loop
const clock = new THREE.Clock();

function animate() {
    const elapsedTime = clock.getElapsedTime();

    
    particlesMesh.rotation.y = elapsedTime * 0.05;
    particlesMesh.rotation.x = elapsedTime * 0.02;

    
    particlesMesh.rotation.x += 0.0001 * mouseY;
    particlesMesh.rotation.y += 0.0001 * mouseX;

    renderer.render(scene, camera);
    window.requestAnimationFrame(animate);
}

animate();

window.addEventListener('resize', () => {
    camera.aspect = window.innerWidth / window.innerHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(window.innerWidth, window.innerHeight);
});

// GSAP Animations for UI Elements
gsap.from(".card", {
    duration: 1,
    y: 50,
    opacity: 0,
    stagger: 0.2,
    ease: "power3.out"
});

// ----------------------------------------------------
// --- NEW CHART.JS INITIALIZATION LOGIC STARTS HERE ---
// ----------------------------------------------------
document.addEventListener('DOMContentLoaded', () => {
    const chartElement = document.getElementById('weightChart');
    if (chartElement) {
        const weightData = JSON.parse(chartElement.dataset.weights);
        const weightDates = JSON.parse(chartElement.dataset.dates);

        if (weightData.length > 0) {
            new Chart(chartElement, {
                type: 'line',
                data: {
                    labels: weightDates,
                    datasets: [{
                        label: 'Weight (kg)',
                        data: weightData,
                        borderColor: '#00f2ff', 
                        backgroundColor: 'rgba(0, 242, 255, 0.1)',
                        tension: 0.4, 
                        pointRadius: 3,
                        pointBackgroundColor: '#00f2ff',
                        borderWidth: 2,
                        fill: true,
                    }]
                },
                options: {
                    responsive: true,
                    maintainAspectRatio: false,
                    plugins: {
                        legend: { display: false },
                        tooltip: { mode: 'index', intersect: false }
                    },
                    scales: {
                        x: { display: false }, 
                        y: { 
                            display: false, 
                            beginAtZero: false 
                        }
                    },
                    layout: {
                        padding: 0
                    }
                }
            });
        }
    }
});