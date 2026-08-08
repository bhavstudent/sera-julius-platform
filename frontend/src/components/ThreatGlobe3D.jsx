import React, { useEffect, useRef } from 'react'
import * as THREE from 'three'

export default function ThreatGlobe3D({ height = '520px' }) {
  const mountRef = useRef(null)

  useEffect(() => {
    const container = mountRef.current
    if (!container) return

    const width = container.clientWidth
    const containerHeight = container.clientHeight || 520

    // 1. Scene, Camera, Renderer
    const scene = new THREE.Scene()
    const camera = new THREE.PerspectiveCamera(45, width / containerHeight, 0.1, 1000)
    camera.position.z = 240

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true })
    renderer.setSize(width, containerHeight)
    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2))
    container.appendChild(renderer.domElement)

    // 2. Real-World Geographic Earth Globe (Round 3D World)
    const globeRadius = 78

    // Lighting
    const ambientLight = new THREE.AmbientLight(0xffffff, 0.8)
    scene.add(ambientLight)
    const dirLight = new THREE.DirectionalLight(0xff2a20, 2.0)
    dirLight.position.set(100, 100, 100)
    scene.add(dirLight)

    // Load High-Res Geographic Earth Map Texture
    const textureLoader = new THREE.TextureLoader()
    const earthTexture = textureLoader.load('https://unpkg.com/three-globe/example/img/earth-dark.jpg')

    // Base Round Earth Mesh with Earth Map Texture
    const globeGeo = new THREE.SphereGeometry(globeRadius, 64, 64)
    const globeMat = new THREE.MeshStandardMaterial({
      map: earthTexture,
      roughness: 0.5,
      metalness: 0.2,
      emissive: 0x330000,
      emissiveIntensity: 0.4
    })
    const baseGlobe = new THREE.Mesh(globeGeo, globeMat)
    scene.add(baseGlobe)

    // Magma Grid / Veins Overlay (Crimson Fire Wireframe)
    const magmaGeo = new THREE.SphereGeometry(globeRadius + 0.3, 48, 48)
    const magmaMat = new THREE.MeshBasicMaterial({
      color: 0xff2a20,
      wireframe: true,
      transparent: true,
      opacity: 0.25
    })
    const magmaMesh = new THREE.Mesh(magmaGeo, magmaMat)
    scene.add(magmaMesh)

    // Crimson Atmosphere Halo (Outer Glow)
    const atmosphereGeo = new THREE.SphereGeometry(globeRadius * 1.15, 32, 32)
    const atmosphereMat = new THREE.MeshBasicMaterial({
      color: 0xff2a20,
      transparent: true,
      opacity: 0.18,
      side: THREE.BackSide
    })
    const atmosphere = new THREE.Mesh(atmosphereGeo, atmosphereMat)
    scene.add(atmosphere)

    // Inner Core Ember Light
    const coreGeo = new THREE.SphereGeometry(globeRadius * 0.95, 32, 32)
    const coreMat = new THREE.MeshBasicMaterial({
      color: 0xff003c,
      transparent: true,
      opacity: 0.25
    })
    const core = new THREE.Mesh(coreGeo, coreMat)
    scene.add(core)

    // 3. Orbiting Asteroid & Debris Cloud
    const particleCount = 300
    const particleGeo = new THREE.BufferGeometry()
    const particlePositions = new Float32Array(particleCount * 3)

    for (let i = 0; i < particleCount; i++) {
      const radius = globeRadius * (1.18 + Math.random() * 0.75)
      const theta = Math.random() * Math.PI * 2
      const phi = Math.acos(Math.random() * 2 - 1)

      particlePositions[i * 3] = radius * Math.sin(phi) * Math.cos(theta)
      particlePositions[i * 3 + 1] = radius * Math.sin(phi) * Math.sin(theta)
      particlePositions[i * 3 + 2] = radius * Math.cos(phi)
    }

    particleGeo.setAttribute('position', new THREE.BufferAttribute(particlePositions, 3))
    const particleMat = new THREE.PointsMaterial({
      color: 0xff3b30,
      size: 2.4,
      transparent: true,
      opacity: 0.8
    })
    const particleCloud = new THREE.Points(particleGeo, particleMat)
    scene.add(particleCloud)

    // 4. Volcanic Threat Nodes
    const threatLocations = [
      { name: 'NYC Core Target', lat: 40.7128, lon: -74.006, color: 0xff2a20 },
      { name: 'London Relay Node', lat: 51.5074, lon: -0.1278, color: 0xff5e3a },
      { name: 'Tokyo STYX Vector', lat: 35.6762, lon: 139.6503, color: 0xff003c },
      { name: 'Singapore Censys Host', lat: 1.3521, lon: 103.8198, color: 0xffb340 },
      { name: 'Berlin Gateway', lat: 52.52, lon: 13.405, color: 0xff2a20 },
      { name: 'Mumbai Relay', lat: 19.076, lon: 72.8777, color: 0xff5e3a },
    ]

    const latLonToVector3 = (lat, lon, radius) => {
      const phi = (90 - lat) * (Math.PI / 180)
      const theta = (lon + 180) * (Math.PI / 180)
      const x = -(radius * Math.sin(phi) * Math.cos(theta))
      const z = radius * Math.sin(phi) * Math.sin(theta)
      const y = radius * Math.cos(phi)
      return new THREE.Vector3(x, y, z)
    }

    const nodeGroup = new THREE.Group()
    threatLocations.forEach(loc => {
      const pos = latLonToVector3(loc.lat, loc.lon, globeRadius + 1.5)

      // Marker Dot
      const dotGeo = new THREE.SphereGeometry(2.5, 16, 16)
      const dotMat = new THREE.MeshBasicMaterial({ color: loc.color })
      const dot = new THREE.Mesh(dotGeo, dotMat)
      dot.position.copy(pos)
      nodeGroup.add(dot)

      // Crimson Ring
      const ringGeo = new THREE.RingGeometry(3, 4.5, 32)
      const ringMat = new THREE.MeshBasicMaterial({
        color: loc.color,
        side: THREE.DoubleSide,
        transparent: true,
        opacity: 0.75
      })
      const ring = new THREE.Mesh(ringGeo, ringMat)
      ring.position.copy(pos)
      ring.lookAt(0, 0, 0)
      nodeGroup.add(ring)
    })
    scene.add(nodeGroup)

    // 5. Crimson Arc Beams
    const createArc = (startLoc, endLoc, color) => {
      const p1 = latLonToVector3(startLoc.lat, startLoc.lon, globeRadius)
      const p2 = latLonToVector3(endLoc.lat, endLoc.lon, globeRadius)
      const mid = p1.clone().add(p2).multiplyScalar(0.5).normalize().multiplyScalar(globeRadius * 1.4)

      const curve = new THREE.QuadraticBezierCurve3(p1, mid, p2)
      const points = curve.getPoints(50)
      const geometry = new THREE.BufferGeometry().setFromPoints(points)

      const material = new THREE.LineBasicMaterial({
        color: color,
        transparent: true,
        opacity: 0.8,
        linewidth: 2.5
      })

      return new THREE.Line(geometry, material)
    }

    scene.add(createArc(threatLocations[0], threatLocations[2], 0xff2a20)) // NYC -> Tokyo
    scene.add(createArc(threatLocations[1], threatLocations[5], 0xff5e3a)) // London -> Mumbai
    scene.add(createArc(threatLocations[3], threatLocations[4], 0xff003c)) // Singapore -> Berlin

    // 6. Mouse Rotation Controls
    let isDragging = false
    let previousMousePosition = { x: 0, y: 0 }

    const onMouseDown = (e) => {
      isDragging = true
      previousMousePosition = { x: e.clientX, y: e.clientY }
    }

    const onMouseMove = (e) => {
      if (!isDragging) return
      const deltaMove = {
        x: e.clientX - previousMousePosition.x,
        y: e.clientY - previousMousePosition.y
      }

      baseGlobe.rotation.y += deltaMove.x * 0.005
      baseGlobe.rotation.x += deltaMove.y * 0.005
      magmaMesh.rotation.y += deltaMove.x * 0.005
      magmaMesh.rotation.x += deltaMove.y * 0.005
      nodeGroup.rotation.y += deltaMove.x * 0.005
      nodeGroup.rotation.x += deltaMove.y * 0.005
      particleCloud.rotation.y += deltaMove.x * 0.002

      previousMousePosition = { x: e.clientX, y: e.clientY }
    }

    const onMouseUp = () => { isDragging = false }

    container.addEventListener('mousedown', onMouseDown)
    window.addEventListener('mousemove', onMouseMove)
    window.addEventListener('mouseup', onMouseUp)

    // 7. Animation Loop
    let animationFrameId
    const animate = () => {
      animationFrameId = requestAnimationFrame(animate)

      if (!isDragging) {
        baseGlobe.rotation.y += 0.0025
        magmaMesh.rotation.y += 0.0025
        nodeGroup.rotation.y += 0.0025
        particleCloud.rotation.y -= 0.001
      }

      renderer.render(scene, camera)
    }
    animate()

    return () => {
      cancelAnimationFrame(animationFrameId)
      container.removeEventListener('mousedown', onMouseDown)
      window.removeEventListener('mousemove', onMouseMove)
      window.removeEventListener('mouseup', onMouseUp)
      if (container.contains(renderer.domElement)) {
        container.removeChild(renderer.domElement)
      }
      renderer.dispose()
    }
  }, [])

  return (
    <div className="threat-globe-card" style={{
      background: 'radial-gradient(circle at 50% 50%, rgba(255, 42, 32, 0.1), rgba(5, 6, 10, 0.95))',
      backdropFilter: 'blur(25px)',
      border: '1px solid rgba(255, 42, 32, 0.35)',
      borderRadius: '16px',
      padding: '24px',
      position: 'relative',
      overflow: 'hidden',
      boxShadow: '0 20px 50px rgba(0,0,0,0.8), 0 0 35px rgba(255, 42, 32, 0.2)'
    }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '14px' }}>
        <div>
          <h3 style={{ margin: 0, fontSize: '1.25rem', color: '#ffffff', display: 'flex', alignItems: 'center', gap: '10px', fontWeight: '800' }}>
            <span style={{ color: '#ff2a20' }}>🔥</span> VOLCANIC CYBER COMMAND GLOBE
          </h3>
          <p style={{ margin: '4px 0 0 0', fontSize: '0.82rem', color: '#94a3b8' }}>
            Interactive 3D threat vector mapping, Censys scan targets & STYX telemetry (Drag to rotate)
          </p>
        </div>
        <span style={{
          background: 'linear-gradient(135deg, #ff2a20, #ff003c)',
          color: '#ffffff',
          padding: '6px 14px',
          borderRadius: '20px',
          fontSize: '11px',
          fontWeight: '800',
          letterSpacing: '0.8px',
          boxShadow: '0 0 15px rgba(255, 42, 32, 0.5)'
        }}>3D CRIMSON GLOBE LIVE</span>
      </div>

      <div ref={mountRef} style={{ width: '100%', height, cursor: 'grab' }} />
    </div>
  )
}

