<template>
  <div class="developers-container">
    <div class="page-header">
      <h1 class="main-title">开发者团队</h1>
      <p class="subtitle">携手打造优质的在线生活服务平台</p>
    </div>
    
    <div class="content-wrapper">
      <!-- 左侧开发者展示 -->
      <div class="team-section">
        <div class="circle-container">
          <div v-for="(developer, index) in developers" 
               :key="developer.id" 
               class="developer-card"
               :class="{ 'active': selectedDeveloper?.id === developer.id }"
               :style="getPositionStyle(index)"
               @click="selectDeveloper(developer)">
            <div class="card-content">
              <div class="avatar-container">
                <img :src="developer.avatar" class="avatar" :alt="developer.name" />
              </div>
              <div class="info-container">
                <h3 class="developer-name">{{ developer.name }}</h3>
                <p class="developer-role">{{ developer.role }}</p>
                <div class="developer-skills">
                  <el-tag v-for="skill in developer.skills" 
                         :key="skill"
                         :type="getRandomType()"
                         class="skill-tag"
                         effect="light">
                    {{ skill }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div class="card-backdrop"></div>
          </div>
        </div>
      </div>

      <!-- 右侧详情区域 -->
      <div class="detail-section" :class="{ 'has-selected': selectedDeveloper }">
        <div class="content-area">
          <transition name="fade" mode="out-in">
            <div v-if="selectedDeveloper" class="developer-detail">
              <h2 class="detail-name">{{ selectedDeveloper.name }}</h2>
              <div class="detail-role">{{ selectedDeveloper.role }}</div>
              <p class="detail-description">{{ selectedDeveloper.description }}</p>
              
              <div class="skills-section">
                <h3 class="section-title">技术栈</h3>
                <div class="skills-grid">
                  <el-tag v-for="skill in selectedDeveloper.skills"
                         :key="skill"
                         :type="getRandomType()"
                         class="detail-skill-tag"
                         effect="light">
                    {{ skill }}
                  </el-tag>
                </div>
              </div>
            </div>
            <div v-else class="placeholder-content">
              <el-icon class="placeholder-icon"><User /></el-icon>
              <p class="placeholder-text">选择开发者查看详细信息</p>
            </div>
          </transition>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue'
import { User } from '@element-plus/icons-vue'

const developers = ref([
  {
    id: 1,
    name: 'CMoments',
    role: '全栈开发工程师',
    avatar: new URL('../assets/avatars/developer1.jpg', import.meta.url).href,
    description: '山西省太原市圪僚沟村财团董事长，挖煤科技集团创始人。5年Vue.js开发经验，专注于用户体验和界面设计。',
    skills: ['Vue.js', 'TypeScript', 'Element Plus']
  },
  {
    id: 2,
    name: '知守',
    role: '全栈开发工程师',
    avatar: new URL('../assets/avatars/developer2.jpg', import.meta.url).href,
    description: '7年Python开发经验，专注于系统架构和性能优化。',
    skills: ['Python', 'FastAPI', 'MySQL']
  },
  {
    id: 3,
    name: 'ʕ•͡•ʔ',
    role: '全栈开发工程师',
    avatar: new URL('../assets/avatars/developer5.jpg', import.meta.url).href,
    description: '4年全栈开发经验，擅长前后端技术整合。',
    skills: ['Node.js', 'React', 'MongoDB']
  },
  {
    id: 4,
    name: '🎤🐈',
    role: '全栈开发工程师',
    avatar: new URL('../assets/avatars/developer4.jpg', import.meta.url).href,
    description: '6年设计经验，注重用户体验和视觉美感。',
    skills: ['Figma', 'Adobe XD', 'Sketch']
  },
  {
    id: 5,
    name: '可惜爱不是写诗',
    role: '全栈开发工程师',
    avatar: new URL('../assets/avatars/developer3.jpg', import.meta.url).href,
    description: '四川地区商界领袖、绵阳财团董事长。DevOps工程师,5年运维经验，专注于自动化部署和系统监控。',
    skills: ['Docker', 'Kubernetes', 'Jenkins']
  }
])

const selectedDeveloper = ref(null)
const tagTypes = ['success', 'warning', 'danger', 'info']

const getRandomType = () => {
  return tagTypes[Math.floor(Math.random() * tagTypes.length)]
}

const getPositionStyle = (index) => {
  const totalDevelopers = developers.value.length
  const radius = 280
  const angle = (index * 2 * Math.PI / totalDevelopers) - Math.PI / 2
  
  return {
    transform: `translate(${radius * Math.cos(angle)}px, ${radius * Math.sin(angle)}px)`
  }
}

const selectDeveloper = (developer) => {
  selectedDeveloper.value = developer
}
</script>

<style scoped>
.developers-container {
  min-height: 100vh;
  background: #ffffff;
  overflow: hidden;
  position: relative;
  color: #2c3e50;
}

.page-header {
  text-align: center;
  padding: 40px 0;
  background: linear-gradient(to right, rgba(66, 184, 131, 0.05), rgba(53, 73, 94, 0.05));
  border-bottom: 1px solid rgba(66, 184, 131, 0.1);
}

.main-title {
  font-size: 2.5em;
  font-weight: 700;
  color: #42b883;
  margin: 0;
}

.subtitle {
  font-size: 1.2em;
  color: #666;
  margin-top: 8px;
}

.content-wrapper {
  width: 100%;
  max-width: 1400px;
  margin: 0 auto;
  display: flex;
  padding: 40px;
  gap: 60px;
}

.circle-container {
  position: relative;
  width: 700px;
  height: 700px;
  margin: 0 auto;
  display: flex;
  justify-content: center;
  align-items: center;
}

.developer-card {
  position: absolute;
  width: 300px;
  height: 300px;
  transform-origin: center center;
  left: 50%;
  top: 50%;
  margin: -110px;
  border-radius: 50%;
  cursor: pointer;
  transition: all 0.4s cubic-bezier(0.4, 0, 0.2, 1);

}

.card-content {
  position: absolute;
  width: 100%;
  height: 100%;
  left: 0;
  top: 0;
  background: #ffffff;
  border-radius: 50%;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  border: 1px solid rgba(66, 184, 131, 0.2);
  box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
  transition: all 0.3s ease;
  overflow: hidden;
}

.card-inner {
  width: 100%;
  padding: 25px;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
}

.avatar-container {
  width: 100px;
  height: 100px;
  margin-bottom: 15px;
  border-radius: 50%;
  overflow: hidden;
  border: 2px solid #42b883;
  flex-shrink: 0;
}

.avatar {
  width: 100%;
  height: 100%;
  object-fit: cover;
}

.developer-name {
  font-size: 1.4em;
  font-weight: 600;
  margin: 4px 0;
  color: #2c3e50;
  line-height: 1.3;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.developer-role {
  font-size: 1em;
  color: #666;
  margin: 4px 0 12px;
  line-height: 1.3;
  max-width: 180px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.developer-skills {
  display: flex;
  flex-wrap: wrap;
  gap: 6px;
  justify-content: center;
  max-width: 180px;
  padding: 0 10px;
}

.skill-tag {
  font-size: 0.85em;
  padding: 4px 10px;
  background: rgba(66, 184, 131, 0.1);
  color: #42b883;
  border-radius: 12px;
  border: 1px solid rgba(66, 184, 131, 0.2);
  white-space: nowrap;
}

.developer-card:hover {
  z-index: 2;
}

.developer-card:hover .card-content {
  border-color: #42b883;
  box-shadow: 0 8px 24px rgba(66, 184, 131, 0.15);
  transform: scale(1.05);
}

.right-section {
  flex: 1;
  display: flex;
  flex-direction: column;
  justify-content: center;
}

.content-area {
  background: #ffffff;
  border-radius: 24px;
  padding: 40px;
  box-shadow: 0 4px 20px rgba(0, 0, 0, 0.05);
  border: 1px solid rgba(66, 184, 131, 0.1);
}

.selected-name {
  font-size: 2.5em;
  margin-bottom: 20px;
  color: #42b883;
  font-weight: 600;
}

.selected-description {
  font-size: 1.2em;
  line-height: 1.6;
  color: #2c3e50;
  margin-bottom: 40px;
}

.music-player,
.player-controls,
.player-info,
.song-name,
.song-artist,
.progress-bar,
.progress {
  display: none;
}

.detail-section {
  opacity: 0;
  transform: translateY(20px);
  transition: all 0.5s ease;
}

.detail-section.has-selected {
  opacity: 1;
  transform: translateY(0);
}

.section-title {
  color: #42b883;
  margin-bottom: 16px;
}

.skills-section {
  margin-bottom: 40px;
}

.skills-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 8px;
}

.detail-skill-tag {
  font-size: 0.9em;
  padding: 4px 12px;
  border-radius: 8px;
}

.placeholder-content {
  text-align: center;
  padding: 60px 0;
  color: rgba(255, 255, 255, 0.5);
}

.placeholder-icon {
  font-size: 48px;
  margin-bottom: 16px;
}

.placeholder-text {
  font-size: 1.2em;
}

.fade-enter-active,
.fade-leave-active {
  transition: opacity 0.3s ease;
}

.fade-enter-from,
.fade-leave-to {
  opacity: 0;
}

@keyframes fadeIn {
  from {
    opacity: 0;
    transform: translateY(10px);
  }
  to {
    opacity: 1;
    transform: translateY(0);
  }
}

@media (max-width: 1200px) {
  .content-wrapper {
    flex-direction: column;
    align-items: center;
    padding: 20px;
  }

  .circle-container {
    width: 600px;
    height: 600px;
  }

  .developer-card {
    width: 200px;
    height: 200px;
    margin: -100px;
  }

  .card-inner {
    padding: 20px;
  }

  .avatar-container {
    width: 90px;
    height: 90px;
    margin-bottom: 12px;
  }

  .developer-name {
    font-size: 1.3em;
    max-width: 160px;
  }

  .developer-role {
    font-size: 0.95em;
    max-width: 160px;
  }
}

@media (max-width: 768px) {
  .main-title {
    font-size: 2em;
  }

  .subtitle {
    font-size: 1em;
  }

  .circle-container {
    width: 500px;
    height: 500px;
  }

  .developer-card {
    width: 180px;
    height: 180px;
    margin: -90px;
  }

  .card-inner {
    padding: 15px;
  }

  .avatar-container {
    width: 80px;
    height: 80px;
    margin-bottom: 10px;
  }

  .developer-name {
    font-size: 1.2em;
    max-width: 140px;
  }

  .developer-role {
    font-size: 0.9em;
    max-width: 140px;
  }

  .skill-tag {
    font-size: 0.8em;
    padding: 3px 8px;
  }
}

.avatar-uploader {
  width: 100%;
  height: 100%;
  cursor: pointer;
}

.upload-area {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  background: rgba(255, 255, 255, 0.6);
  transition: all 0.3s ease;
}

.upload-area:hover {
  background: rgba(255, 255, 255, 0.8);
}

.upload-area.has-avatar {
  background: none;
}

.avatar-uploader-icon {
  font-size: 28px;
  color: #8c939d;
  transition: all 0.3s;
}

.upload-area:hover .avatar-uploader-icon {
  color: #42b883;
  transform: scale(1.1);
}

.detail-description {
  font-size: 1.4em;
  line-height: 1.6;
  color: #2c3e50;
  margin: 20px 0 40px;
  padding: 15px;
  background: rgba(66, 184, 131, 0.05);
  border-radius: 12px;
  border-left: 4px solid #42b883;
}

.developer-detail {
  h2.detail-name {
    font-size: 2.5em;
    margin-bottom: 10px;
    color: #42b883;
    font-weight: 600;
  }

  .detail-role {
    font-size: 1.2em;
    color: #666;
    margin-bottom: 20px;
  }
}
</style> 