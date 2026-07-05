use crate::{
    BenchmarkRecord,
    ModelScore,
};

pub struct BenchmarkEngine;

impl BenchmarkEngine {

    pub fn new() -> Self {

        Self

    }

    pub fn rank(

        &self,

        records: &[BenchmarkRecord],

    ) -> Vec<ModelScore> {

        let mut scores = Vec::new();

        for record in records {

            let m = &record.metrics;

            let score =

                m.accuracy * 50.0 +

                m.trust_score * 30.0 -

                (m.latency_ms as f32 * 0.02) -

                (m.ram_mb as f32 * 0.002) -

                m.power_watts;

            scores.push(

                ModelScore {

                    provider: record.provider.clone(),

                    model: record.model.clone(),

                    score,

                }

            );

        }

        scores.sort_by(

            |a,b|

            b.score.partial_cmp(&a.score).unwrap()

        );

        scores

    }

}
