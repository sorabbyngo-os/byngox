#[derive(Debug, Clone)]
pub struct ProgressTracker {
    total_steps: usize,
    completed_steps: usize,
}

impl ProgressTracker {
    pub fn new(total_steps: usize) -> Self {
        Self {
            total_steps,
            completed_steps: 0,
        }
    }

    pub fn advance(&mut self) {
        if self.completed_steps < self.total_steps {
            self.completed_steps += 1;
        }
    }

    pub fn completed(&self) -> usize {
        self.completed_steps
    }

    pub fn total(&self) -> usize {
        self.total_steps
    }

    pub fn finished(&self) -> bool {
        self.completed_steps >= self.total_steps
    }

    pub fn percentage(&self) -> f32 {
        if self.total_steps == 0 {
            100.0
        } else {
            (self.completed_steps as f32 / self.total_steps as f32) * 100.0
        }
    }
}
